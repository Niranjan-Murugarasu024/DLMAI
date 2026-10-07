"""
Saaty Analytic Hierarchy Process (AHP) Engine for South India DLMAI.
Computes principal eigenvector weights from a pairwise comparison matrix and validates Consistency Ratio (CR < 0.10).
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


SAATY_RANDOM_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}


@dataclass
class AHPValidationResult:
    criteria: List[str]
    weights: Dict[str, float]
    lambda_max: float
    consistency_index: float
    random_index: float
    consistency_ratio: float
    is_consistent: bool


def calculate_ahp_weights(matrix: np.ndarray, criteria: List[str]) -> AHPValidationResult:
    """
    matrix: n x n reciprocal pairwise comparison matrix
    criteria: list of n criteria names
    """
    n = len(criteria)
    if matrix.shape != (n, n):
        raise ValueError(f"Matrix shape {matrix.shape} does not match {n} criteria")

    # Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_idx = int(np.argmax(np.real(eigenvalues)))
    lambda_max = float(np.real(eigenvalues[max_idx]))
    principal_ev = np.real(eigenvectors[:, max_idx])

    # Normalize priority vector
    weights_arr = principal_ev / np.sum(principal_ev)
    weights_dict = {crit: round(float(w), 6) for crit, w in zip(criteria, weights_arr)}

    # Consistency checks
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = SAATY_RANDOM_INDEX.get(n, 1.32)
    cr = ci / ri if ri > 0 else 0.0

    return AHPValidationResult(
        criteria=criteria,
        weights=weights_dict,
        lambda_max=round(lambda_max, 6),
        consistency_index=round(ci, 6),
        random_index=ri,
        consistency_ratio=round(cr, 6),
        is_consistent=(cr < 0.10)
    )
