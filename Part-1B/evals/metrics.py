"""Independent evaluation metric scorers across three dimensions.

Dimension A: Schema Adherence (100% target)
Dimension B: Deterministic Invariant Compliance (100% target)
Dimension C: Semantic Quality (Precision >=80%, Recall >=80%, F1 >=80%, FPR <=15%)

Cites: Part-1B/specs/001-code-review-assistant/plan.md (Evaluation Strategy)
"""

from typing import Any


def compute_schema_adherence(results: list[dict[str, Any]]) -> float:
    """Compute Dimension A: Percentage of model outputs adhering strictly to the JSON schema."""
    if not results:
        return 1.0

    valid_count = sum(1 for r in results if r.get("is_schema_valid", False))
    return round(valid_count / len(results), 4)


def compute_invariant_compliance(results: list[dict[str, Any]]) -> float:
    """Compute Dimension B: Percentage of outputs satisfying deterministic invariants."""
    if not results:
        return 1.0

    compliant_count = sum(1 for r in results if r.get("is_invariant_compliant", False))
    return round(compliant_count / len(results), 4)


def compute_percentile(values: list[int | float], percentile: float = 95.0) -> float:
    """Compute the given percentile (e.g. 95th) of a list of numeric values using linear interpolation."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (percentile / 100.0)
    f = int(k)
    c = f + 1
    if c < len(sorted_vals):
        return round(float(sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])), 2)
    return round(float(sorted_vals[f]), 2)


def compute_semantic_metrics(predictions: list[bool], ground_truth: list[bool]) -> dict[str, float]:
    """Compute Dimension C: Precision, Recall, F1 Score, and False-Positive Rate.

    Args:
        predictions: Boolean list where True indicates a defect was predicted (FAIL / finding present).
        ground_truth: Boolean list where True indicates a genuine defect exists (is_clean == False).
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground_truth lists must have identical lengths.")

    if not predictions:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "false_positive_rate": 0.0,
            "tp": 0,
            "fp": 0,
            "fn": 0,
            "tn": 0,
        }

    tp = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is True and g is True)
    fp = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is True and g is False)
    fn = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is False and g is True)
    tn = sum(1 for p, g in zip(predictions, ground_truth, strict=False) if p is False and g is False)

    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if sum(ground_truth) == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else (1.0 if sum(ground_truth) == 0 else 0.0)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }
