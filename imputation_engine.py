"""
Data quality & imputation engine — DLMAI Layer 3.

Runs AFTER Layer 2's district crosswalk and inheritance (district_crosswalk.py's
InheritanceResolver) have already filled whatever they can for newly-carved
districts. This layer handles values that are genuinely missing in the
source data itself, using a defined hierarchy rather than ad hoc guessing:

  1. Same-district trend interpolation (needs 2+ time points for that
     district on that indicator)
  2. State-mean substitution (mean of the same indicator across other
     districts in the same state that do have a value)
  3. Nearest-neighbor imputation (mean of the indicator among the k most
     population-similar districts that do have a value)
  4. Leave it missing and flag it -- never silently fabricate a number
     that survived none of the above

Every fill is recorded in a parallel confidence mask, never silently folded
into the data as if it were as solid as a native measurement. That mask is
what lets a later step recompute the index with and without imputed cells
and report a confidence band, instead of presenting one number as if every
district's score rested on equally solid ground.
"""

import statistics
from dataclasses import dataclass, field

STATUS_NATIVE = "native"
STATUS_TREND = "trend_interpolated"
STATUS_STATE_MEAN = "state_mean"
STATUS_NEAREST_NEIGHBOR = "nearest_neighbor"
STATUS_STILL_MISSING = "still_missing"


@dataclass
class ImputationResult:
    filled: dict   # lgd_code -> {indicator_id: value}
    mask: dict     # lgd_code -> {indicator_id: status string}


def trend_interpolate(time_series: dict, target_year: int, min_value=None, max_value=None):
    """
    time_series: {year: value_or_None} for ONE district, ONE indicator.
    Linear interpolation between the two nearest known points; linear
    extrapolation from the two most recent known points if target_year is
    beyond the latest one. Returns None if fewer than 2 known points exist
    -- there's no honest way to interpolate a trend from a single point.

    min_value/max_value: optional bounds clamp applied to the result.
    Linear EXTRAPOLATION specifically (not interpolation between two real
    points) can produce physically impossible values for a bounded
    indicator -- e.g. a percentage trending downward over two known years
    will eventually extrapolate past 0 into negative territory the
    further out you project, which no real percentage can do. Pass
    min_value=0 (and/or a sensible max_value, e.g. 100 for a percentage)
    for any indicator with a known physical bound; left as None by
    default so this stays a generic building block, not specific to one
    indicator's bounds.
    """
    known = sorted((yr, v) for yr, v in time_series.items() if v is not None)
    if len(known) < 2:
        return None
    if target_year <= known[0][0]:
        (y0, v0), (y1, v1) = known[0], known[1]
    elif target_year >= known[-1][0]:
        (y0, v0), (y1, v1) = known[-2], known[-1]
    else:
        (y0, v0), (y1, v1) = known[0], known[-1]
        for i in range(len(known) - 1):
            if known[i][0] <= target_year <= known[i + 1][0]:
                (y0, v0), (y1, v1) = known[i], known[i + 1]
                break
    if y1 == y0:
        result = v0
    else:
        slope = (v1 - v0) / (y1 - y0)
        result = v0 + slope * (target_year - y0)
    if min_value is not None:
        result = max(result, min_value)
    if max_value is not None:
        result = min(result, max_value)
    return result


class ImputationEngine:
    def __init__(self, district_state_map: dict, district_population: dict,
                 nearest_neighbor_k: int = 5):
        """
        district_state_map: lgd_code -> state_name. Build this from a
            DistrictCrosswalk instance: {d.lgd_code: d.state_name for d
            in crosswalk.districts} -- never maintain a second, separate
            copy of the district/state relationship.
        district_population: lgd_code -> population, the similarity
            covariate used for nearest-neighbor matching. Swap this for a
            different covariate (urbanization rate, healthcare bed count,
            whatever you trust more for a given indicator) if population
            isn't the right similarity axis.
        """
        self.district_state_map = district_state_map
        self.district_population = district_population
        self.k = nearest_neighbor_k

    def impute(self, data: dict, indicator_ids: list,
               time_series_data: dict = None, target_year: int = None) -> ImputationResult:
        """
        data: lgd_code -> {indicator_id: value_or_None}
        time_series_data: optional lgd_code -> {indicator_id: {year: value}},
            attempted first for any indicator where it's supplied.
        """
        filled = {code: dict(vals) for code, vals in data.items()}
        mask = {code: {} for code in data}

        for indicator_id in indicator_ids:
            # --- Step 1: trend interpolation ---
            if time_series_data:
                for code in filled:
                    if filled[code].get(indicator_id) is not None:
                        continue
                    ts = time_series_data.get(code, {}).get(indicator_id)
                    if ts:
                        interpolated = trend_interpolate(ts, target_year)
                        if interpolated is not None:
                            filled[code][indicator_id] = interpolated
                            mask[code][indicator_id] = STATUS_TREND

            for code in filled:
                if indicator_id not in mask[code] and filled[code].get(indicator_id) is not None:
                    mask[code][indicator_id] = STATUS_NATIVE

            # Snapshot of "real" evidence -- native or trend-derived only --
            # taken BEFORE either fallback step runs. Both step 2 and step 3
            # read exclusively from this snapshot when deciding what counts
            # as a donor, never from each other's output. Without this, a
            # district's state-mean fill could quietly become eligible as a
            # nearest-neighbor donor for a different state's district one
            # step later -- one imputed value justifying another, with the
            # uncertainty compounding silently instead of staying contained.
            donor_pool = {
                code: vals[indicator_id]
                for code, vals in filled.items()
                if vals.get(indicator_id) is not None
                and mask[code].get(indicator_id) in (STATUS_NATIVE, STATUS_TREND)
            }

            # --- Step 2: state-mean substitution (donors: snapshot only) ---
            state_values = {}
            for code, v in donor_pool.items():
                state = self.district_state_map.get(code)
                state_values.setdefault(state, []).append(v)
            state_means = {state: statistics.mean(vs) for state, vs in state_values.items()}

            for code in filled:
                if filled[code].get(indicator_id) is not None:
                    continue
                state = self.district_state_map.get(code)
                if state in state_means:
                    filled[code][indicator_id] = state_means[state]
                    mask[code][indicator_id] = STATUS_STATE_MEAN

            # --- Step 3: nearest-neighbor by population (donors: same snapshot) ---
            known_pop_values = [
                (self.district_population.get(c), v)
                for c, v in donor_pool.items()
                if self.district_population.get(c) is not None
            ]
            for code in filled:
                if filled[code].get(indicator_id) is not None:
                    continue
                target_pop = self.district_population.get(code)
                if target_pop is None or not known_pop_values:
                    mask[code][indicator_id] = STATUS_STILL_MISSING
                    continue
                neighbors = sorted(known_pop_values, key=lambda pv: abs(pv[0] - target_pop))[: self.k]
                filled[code][indicator_id] = statistics.mean(v for _, v in neighbors)
                mask[code][indicator_id] = STATUS_NEAREST_NEIGHBOR

        return ImputationResult(filled=filled, mask=mask)


def completeness_report(mask: dict, indicator_ids: list) -> dict:
    """
    Per-indicator breakdown of how each value was actually obtained.
    Look at this BEFORE trusting any composite score built on top of it --
    an indicator that's 80% nearest-neighbor-imputed is not contributing
    the same kind of evidence as one that's 95% native.
    """
    report = {ind: {STATUS_NATIVE: 0, STATUS_TREND: 0, STATUS_STATE_MEAN: 0,
                     STATUS_NEAREST_NEIGHBOR: 0, "inherited": 0, STATUS_STILL_MISSING: 0}
              for ind in indicator_ids}
    for lgd_code, ind_statuses in mask.items():
        for ind, status in ind_statuses.items():
            if ind not in report:
                continue
            if status.startswith("inherited_from_"):
                report[ind]["inherited"] += 1
            elif status in report[ind]:
                report[ind][status] += 1
    return report


def print_completeness_report(report: dict, total_districts: int):
    print(f"{'Indicator':30s} {'native':>8s} {'trend':>7s} {'st.mean':>8s} "
          f"{'nn':>5s} {'inherit':>8s} {'missing':>8s}")
    for ind, counts in report.items():
        native_pct = 100 * counts[STATUS_NATIVE] / total_districts
        print(f"{ind:30s} {counts[STATUS_NATIVE]:>8d} {counts[STATUS_TREND]:>7d} "
              f"{counts[STATUS_STATE_MEAN]:>8d} {counts[STATUS_NEAREST_NEIGHBOR]:>5d} "
              f"{counts['inherited']:>8d} {counts[STATUS_STILL_MISSING]:>8d}"
              f"   ({native_pct:.0f}% native)")
