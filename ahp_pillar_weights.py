"""
AHP pillar-weighting tool for the District-Level Market Attractiveness Index (DLMAI).

Computes pillar weights from a Saaty pairwise comparison matrix via the
eigenvector method, validates consistency (CR < 0.10), and can aggregate
judgments from multiple domain experts into a single panel matrix.

The matrix below is a STARTING TEMPLATE, not a final answer. Replace it with
judgments from your own pharma BD / market access panel before using these
weights for anything real. See the bottom of this file for how to do that.
"""

import numpy as np

# Saaty's Random Index (RI) — average CI of randomly generated matrices,
# used to normalize the Consistency Index into a Consistency Ratio.
RI_TABLE = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def compute_ahp_weights(matrix, labels):
    """
    matrix: n x n numpy array, Saaty pairwise comparisons (reciprocal, diag=1)
    labels: list of n pillar names, same order as matrix rows/cols
    Returns a dict with weights, lambda_max, CI, CR, consistency flag,
    and a per-row inconsistency diagnostic to help locate a bad judgment.
    """
    n = matrix.shape[0]
    eigvals, eigvecs = np.linalg.eig(matrix)
    max_idx = np.argmax(eigvals.real)
    lam_max = eigvals[max_idx].real
    w = eigvecs[:, max_idx].real
    w = w / w.sum()

    CI = (lam_max - n) / (n - 1)
    RI = RI_TABLE.get(n, 1.49)
    CR = CI / RI if RI > 0 else 0.0

    # Per-row diagnostic: how far each row deviates from M @ w == lambda_max * w.
    # Rows with the largest deviation are the best place to start if CR fails.
    residual = matrix @ w - lam_max * w
    diagnostics = sorted(zip(labels, np.abs(residual)), key=lambda x: -x[1])

    return {
        "weights": dict(sorted(zip(labels, w), key=lambda x: -x[1])),
        "lambda_max": lam_max,
        "CI": CI,
        "RI": RI,
        "CR": CR,
        "consistent": CR < 0.10,
        "diagnostics": diagnostics,
    }


def aggregate_expert_matrices(matrices):
    """
    Standard AHP group-aggregation: element-wise geometric mean across
    multiple experts' pairwise matrices. Use this once you have 3-5 panel
    members' independently filled matrices, instead of relying on one
    person's judgment.
    """
    stacked = np.stack(matrices)
    return np.exp(np.mean(np.log(stacked), axis=0))


def print_report(result, title="AHP Pillar Weights"):
    print(f"\n{title}")
    print("-" * len(title))
    for label, w in result["weights"].items():
        print(f"  {label:42s} {w*100:5.2f}%")
    print(f"\n  lambda_max = {result['lambda_max']:.4f}   "
          f"CI = {result['CI']:.4f}   CR = {result['CR']:.4f}")
    status = "PASS (CR < 0.10)" if result["consistent"] else "FAIL — revisit judgments below CR >= 0.10"
    print(f"  Consistency: {status}")
    if not result["consistent"]:
        print("\n  Largest-deviation pillars (check these comparisons first):")
        for label, dev in result["diagnostics"][:3]:
            print(f"    {label:42s} deviation {dev:.4f}")


if __name__ == "__main__":
    # --- STARTING TEMPLATE: replace with your panel's actual judgments ---
    # Order chosen by domain reasoning (most to least fundamental driver of
    # pharma market attractiveness). Pillar 5 is deliberately judged as
    # consistently less important given its lower data confidence
    # (see Section 1.1 of the framework doc) — this is what pulls its
    # weight down to a small-but-nonzero share, by honest judgment rather
    # than an after-the-fact cap.
    labels = [
        "P1 Demand & disease burden",
        "P3 Healthcare infrastructure",
        "P2 Economic access & affordability",
        "P4 Distribution & retail density",
        "P6 Regulatory & scheme environment",
        "P7 Growth momentum",
        "P5 Industry presence & supply depth",
    ]
    n = len(labels)
    M = np.ones((n, n))
    # (row_index, col_index): row pillar this many times MORE important
    # than column pillar, on Saaty's 1-9 scale.
    judgments = {
        (0, 1): 2, (0, 2): 3, (0, 3): 3, (0, 4): 5, (0, 5): 5, (0, 6): 7,
        (1, 2): 2, (1, 3): 3, (1, 4): 4, (1, 5): 5, (1, 6): 6,
        (2, 3): 2, (2, 4): 3, (2, 5): 3, (2, 6): 5,
        (3, 4): 2, (3, 5): 2, (3, 6): 4,
        (4, 5): 1, (4, 6): 3,
        (5, 6): 3,
    }
    for (i, j), v in judgments.items():
        M[i, j] = v
        M[j, i] = 1 / v

    result = compute_ahp_weights(M, labels)
    print_report(result, title="DLMAI Pillar Weights — v1.1 starting template")

    # --- How to replace this with real panel judgments ---
    # 1. Give each of 3-5 domain experts the same blank 7x7 matrix and the
    #    Saaty 1-9 scale; have each fill only the upper triangle independently.
    # 2. Build one numpy matrix per expert (same code as above).
    # 3. combined = aggregate_expert_matrices([expert1_M, expert2_M, ...])
    # 4. result = compute_ahp_weights(combined, labels)
    # 5. If CR >= 0.10, print_report() tells you which pillar's comparisons
    #    to take back to the panel for a second pass.
