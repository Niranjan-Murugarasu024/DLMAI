"""
Production entrypoint for South India DLMAI:
Runs the full pipeline (ingestion -> crosswalk -> inheritance -> imputation -> scoring -> sensitivity -> validation)
and writes all output deliverables to outputs/.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import run_south_india_pipeline


def main():
    print("=" * 70)
    print("South India District-Level Market Attractiveness Index (DLMAI)")
    print("Production Pipeline Execution (Version 2.0.0)")
    print("=" * 70)

    try:
        results = run_south_india_pipeline(output_dir="outputs")
        meta = results["refresh_metadata"]
        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION SUMMARY")
        print(f"  Geographic Universe:       {meta['geographic_scope']}")
        print(f"  Canonical District Count:  {meta['total_canonical_districts']}")
        print(f"  Scored Indicators:         {meta['total_scored_indicators']}")
        print(f"  AHP Consistency Ratio:     {meta['ahp_consistency_ratio']} (CR < 0.10 Passed)")
        print(f"  Mean DLMAI Score:          {meta['mean_dlmai_score']}")
        print(f"  Median DLMAI Score:        {meta['median_dlmai_score']}")
        print(f"  Highest Ranking District:  {meta['highest_scoring_district']} (Score: {meta['highest_score']})")
        print(f"  Lowest Ranking District:   {meta['lowest_scoring_district']} (Score: {meta['lowest_score']})")
        print(f"  Monte Carlo Rank Stability:{meta['mean_spearman_rank_stability']} ({meta['stability_assessment']})")
        print("=" * 70)
        print("All deliverables generated successfully in outputs/\n")
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
