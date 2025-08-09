"""
Structured CPDs Utilities for Kor.ai Bayesian Risk Engine

Provides parameterized generators for TabularCPDs using softmax/logistic links
with small parameter sets, enabling calibration and monotonic constraints.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Sequence, Tuple, Optional

import math
from pgmpy.factors.discrete import TabularCPD


def _softmax(scores: Sequence[float]) -> List[float]:
    """Numerically stable softmax with empty-sequence protection."""
    if not scores:
        return []
    max_s = max(scores)
    exps = [math.exp(s - max_s) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]


def _state_to_feature(state_idx: int, num_states: int = 3) -> float:
    """Map ordinal state index to a normalized feature in [0,1].

    Returns 0.0 for degenerate cases (num_states <= 1) to avoid division by zero.
    """
    if num_states <= 1:
        return 0.0
    return float(state_idx) / float(num_states - 1)


def _compute_normalized_score(
    parents: List[str],
    combo: Tuple[int, ...],
    evidence_card: List[int],
    parent_weights: Dict[str, float],
) -> float:
    """Compute weighted normalized score in [0,1] for a given parent-state combo."""
    score = sum(
        parent_weights.get(parent_name, 0.0) * _state_to_feature(state_idx, card)
        for parent_name, state_idx, card in zip(parents, combo, evidence_card)
    )
    total_w = sum(max(0.0, w) for w in parent_weights.values()) or 1.0
    return min(max(score / total_w, 0.0), 1.0)


@dataclass
class SoftmaxCPDParams:
    """Parameters for a softmax-based CPD over 3 classes.

    - parent_weights: weight per parent contributing to the scalar evidence score
    - class_bias: bias per class [no_intent, potential, clear]
    - class_gain: gain per class controlling slope
    - enforce_monotonic_for: parents required to have non-negative weights
    """

    parent_weights: Dict[str, float]
    class_bias: Tuple[float, float, float] = (0.0, -0.25, -0.5)
    class_gain: Tuple[float, float, float] = (1.0, 2.0, 3.0)
    enforce_monotonic_for: Tuple[str, ...] = tuple()

    def sanitized(self) -> "SoftmaxCPDParams":
        weights = dict(self.parent_weights)
        for p in self.enforce_monotonic_for:
            if weights.get(p, 0.0) < 0.0:
                weights[p] = 0.0
        return SoftmaxCPDParams(
            parent_weights=weights,
            class_bias=self.class_bias,
            class_gain=self.class_gain,
            enforce_monotonic_for=self.enforce_monotonic_for,
        )


def validate_softmax_params(
    params: SoftmaxCPDParams, validation_data: Optional[Dict] = None
) -> bool:
    """Basic validation for softmax parameters.

    - Ensures enforced-monotonic parents have non-negative weights
    - Ensures total positive weight is non-zero
    - Optionally: compare against simple bounds in validation_data
    """
    p = params.sanitized()
    if sum(max(0.0, w) for w in p.parent_weights.values()) <= 0.0:
        return False
    for name in p.enforce_monotonic_for:
        if p.parent_weights.get(name, 0.0) < 0.0:
            return False
    return True


def tune_softmax_params(
    params: SoftmaxCPDParams, training_data: Optional[Dict] = None
) -> SoftmaxCPDParams:
    """Placeholder tuner: returns sanitized params; adjust access-related weight slightly up.
    Integrate with CPDCalibrator for data-driven tuning when available.
    """
    p = params.sanitized()
    for k in list(p.parent_weights.keys()):
        if any(tag in k for tag in ("mnpi", "access", "state_information")):
            p.parent_weights[k] = max(0.0, p.parent_weights[k]) * 1.05
    return p


def generate_softmax_cpd(
    variable: str,
    parents: List[str],
    evidence_card: List[int],
    params: SoftmaxCPDParams,
) -> TabularCPD:
    """Generate a TabularCPD for a 3-state variable using a softmax over a scalar score.
    The scalar score is a weighted sum of normalized parent states (0..1).
    Class logits are linear functions of the score.
    """
    if len(parents) != len(evidence_card):
        raise ValueError(
            f"Number of parents ({len(parents)}) must match length of evidence_card ({len(evidence_card)})"
        )
    params = params.sanitized()

    combos = list(product(*[range(c) for c in evidence_card]))
    rows_no, rows_mid, rows_hi = [], [], []

    for combo in combos:
        # Compute normalized score in [0,1]
        score = _compute_normalized_score(parents, combo, evidence_card, params.parent_weights)
        b0, b1, b2 = params.class_bias
        g0, g1, g2 = params.class_gain
        z0 = b0 + g0 * (1.0 - score)
        z1 = b1 + g1 * (score - 0.5)
        z2 = b2 + g2 * score
        p0, p1, p2 = _softmax([z0, z1, z2])
        rows_no.append(p0)
        rows_mid.append(p1)
        rows_hi.append(p2)

    values = [rows_no, rows_mid, rows_hi]
    return TabularCPD(
        variable=variable,
        variable_card=3,
        evidence=parents,
        evidence_card=evidence_card,
        values=values,
    )


def generate_linear_aggregate_cpd(
    variable: str, parents: List[str], evidence_card: List[int], weight: float = 1.0
) -> TabularCPD:
    """Aggregate multiple 3-state parents into a 3-state factor via softmax on summed score.

    All parents contribute equally by default; weight adjusts influence strength.
    """
    parent_weights = {p: weight for p in parents}
    params = SoftmaxCPDParams(
        parent_weights=parent_weights,
        class_bias=(0.5, 0.0, -0.5),  # bias slightly toward no/medium
        class_gain=(1.0, 2.0, 3.0),
    )
    return generate_softmax_cpd(variable, parents, evidence_card, params)


# Skeleton calibrator (placeholders)
@dataclass
class CPDCalibrator:
    """Placeholder for data-driven calibration of structured CPDs.

    In a full implementation, this would fit parameters to labeled data.
    """

    learned_params: Dict[str, SoftmaxCPDParams] = field(default_factory=dict)

    def fit_latent_intent(
        self, model_name: str, parents: List[str], evidence: List[List[int]], labels: List[int]
    ) -> SoftmaxCPDParams:
        """Fit parameters (placeholder). In practice, use multinomial logistic regression.
        Enforce monotonicity for certain parents by clipping negative weights.
        """
        # Placeholder heuristic: start from equal weights; increase weights for MNPI-like signals
        base_w = {p: 1.0 for p in parents}
        for p in parents:
            if any(k in p for k in ["mnpi", "state_information", "news_timing", "access"]):
                base_w[p] = 1.5
        params = SoftmaxCPDParams(
            parent_weights=base_w,
            class_bias=(0.25, -0.1, -0.5),
            class_gain=(1.0, 2.0, 3.5),
            enforce_monotonic_for=tuple([p for p in parents if "mnpi" in p or "access" in p]),
        ).sanitized()
        self.learned_params[model_name] = params
        return params