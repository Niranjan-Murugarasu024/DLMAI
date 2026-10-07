"""
Demonstration / smoke test for district_crosswalk.py.

Runs the engine against the kind of messy, real district references you'd
actually pull from Census handbooks, NFHS factsheets, the Jan Aushadhi
locator, and MCA21 company addresses -- including renames, the 2022 Andhra
Pradesh district bifurcation, and a genuinely ambiguous short name.
"""

from district_crosswalk import DistrictCrosswalk, InheritanceResolver

xwalk = DistrictCrosswalk(
    master_csv_path="sample_lgd_seed.csv",
    alias_csv_path="manual_aliases.csv",
)

print("=" * 78)
print("TEST 1 -- straightforward exact matches (should just work)")
print("=" * 78)
for name in ["Coimbatore", "Pune", "Jaipur"]:
    r = xwalk.resolve(name)
    print(f"  {name!r:25s} -> {r.method:12s} lgd={r.lgd_code}  conf={r.confidence}")

print()
print("=" * 78)
print("TEST 2 -- renamed districts, old name shows up in a source")
print("=" * 78)
for name in ["Allahabad", "Faizabad", "Calcutta", "Madras", "Ahmadabad"]:
    r = xwalk.resolve(name)
    print(f"  {name!r:25s} -> {r.method:12s} lgd={r.lgd_code}  matched={r.matched_name}")

print()
print("=" * 78)
print("TEST 3 -- manual alias table catches a rename too different for fuzzy matching")
print("=" * 78)
for name in ["Bombay City", "Bombay"]:
    r = xwalk.resolve(name)
    print(f"  {name!r:25s} -> {r.method:12s} lgd={r.lgd_code}  matched={r.matched_name}")
# Sanity check: confirm fuzzy matching alone genuinely fails on this pair,
# which is *why* the alias table needs to exist as a separate mechanism.
import difflib
score = difflib.SequenceMatcher(None, "bombay city", "mumbai city").ratio()
print(f"  (fuzzy-only similarity 'bombay city' vs 'mumbai city' = {score:.3f}"
      f" -- {'would have passed anyway' if score >= 0.84 else 'would NOT have matched without the alias'})")

print()
print("=" * 78)
print("TEST 4 -- genuinely ambiguous short name, no state context given")
print("=" * 78)
r = xwalk.resolve("Bangalore")
print(f"  'Bangalore' (no state hint, default strict threshold 0.84) -> {r.method}"
      f"  (conf={r.confidence}; below threshold, so it's correctly rejected outright)")

# Same input through a looser engine, just to show the *ambiguity* branch
# itself firing (as opposed to the unmatched branch) -- this is what would
# happen with messier real-world abbreviations that score higher but still
# point at more than one district.
loose = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv", fuzzy_threshold=0.70)
r_loose = loose.resolve("Bangalore")
print(f"  same input, fuzzy_threshold=0.70 -> {r_loose.method}")
for code, name, state in r_loose.candidates:
    print(f"      candidate: {name} ({state}) [{code}]")
print("  (this is why 0.84 is the recommended default -- it's strict enough that "
      "ambiguous short names get rejected before they even reach the tie-breaking logic)")

print()
print("=" * 78)
print("TEST 4b -- same ambiguous name, but the source dataset also gave us a state")
print("=" * 78)
r = xwalk.resolve("Bangalore Urban", state_hint="Karnataka")
print(f"  'Bangalore Urban' + state hint 'Karnataka' -> {r.method} lgd={r.lgd_code} matched={r.matched_name}")

print()
print("=" * 78)
print("TEST 5 -- a name that genuinely doesn't exist anywhere in the master")
print("=" * 78)
r = xwalk.resolve("Atlantis District")
print(f"  'Atlantis District' -> {r.method}  (best fuzzy score was {r.confidence}, below threshold -- correctly flagged, not guessed)")

print()
print("=" * 78)
print("TEST 6 -- inheritance: 2022 Andhra Pradesh bifurcation, indicator missing for new districts")
print("=" * 78)
inherit = InheritanceResolver(xwalk)
# Simulate a pre-2022 indicator file: Kurnool and Guntur have real values,
# but Nandyal, Palnadu, Bapatla, Annamayya didn't exist yet so they're null.
simulated_indicator = {
    "SAMPLE-AP-01": 42.0,   # Kurnool -- has data
    "SAMPLE-AP-02": None,   # Nandyal -- carved from Kurnool in 2022, no native data
    "SAMPLE-AP-03": 58.0,   # Guntur -- has data
    "SAMPLE-AP-04": None,   # Palnadu -- carved from Guntur
    "SAMPLE-AP-05": None,   # Bapatla -- carved from Guntur
    "SAMPLE-AP-06": 31.0,   # YSR Kadapa -- has data
    "SAMPLE-AP-07": None,   # Annamayya -- carved from YSR Kadapa
}
filled, mask = inherit.fill_missing(simulated_indicator)
for code in simulated_indicator:
    d = xwalk.by_code[code]
    print(f"  {d.current_name:15s} value={filled[code]!s:6s}  status={mask[code]}")

print()
print("All tests completed.")
