"""Unit tests for independent evaluation metric scorers (T042)."""


def test_schema_adherence_scorer():
    from evals.metrics import compute_schema_adherence

    # 10 valid responses
    valid_results = [{"is_schema_valid": True} for _ in range(10)]
    assert compute_schema_adherence(valid_results) == 1.0

    # 9 valid, 1 invalid
    mixed_results = [{"is_schema_valid": True} for _ in range(9)] + [{"is_schema_valid": False}]
    assert compute_schema_adherence(mixed_results) == 0.9

    # Empty list
    assert compute_schema_adherence([]) == 1.0


def test_invariant_compliance_scorer():
    from evals.metrics import compute_invariant_compliance

    valid_results = [{"is_invariant_compliant": True} for _ in range(5)]
    assert compute_invariant_compliance(valid_results) == 1.0

    mixed_results = [
        {"is_invariant_compliant": True},
        {"is_invariant_compliant": False},
    ]
    assert compute_invariant_compliance(mixed_results) == 0.5


def test_semantic_metrics_scorer_perfect():
    from evals.metrics import compute_semantic_metrics

    # TP = 4, TN = 4, FP = 0, FN = 0
    predictions = [True, True, True, True, False, False, False, False]
    ground_truth = [True, True, True, True, False, False, False, False]

    metrics = compute_semantic_metrics(predictions, ground_truth)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["false_positive_rate"] == 0.0


def test_semantic_metrics_scorer_with_fp_and_fn():
    from evals.metrics import compute_semantic_metrics

    # TP = 3, FP = 1, FN = 1, TN = 3
    # predictions:  [1, 1, 1, 1, 0, 0, 0, 0]
    # ground_truth: [1, 1, 1, 0, 1, 0, 0, 0]
    predictions = [True, True, True, True, False, False, False, False]
    ground_truth = [True, True, True, False, True, False, False, False]

    metrics = compute_semantic_metrics(predictions, ground_truth)
    # Precision = 3 / (3 + 1) = 0.75
    assert metrics["precision"] == 0.75
    # Recall = 3 / (3 + 1) = 0.75
    assert metrics["recall"] == 0.75
    # F1 = 0.75
    assert metrics["f1_score"] == 0.75
    # FPR = FP / (FP + TN) = 1 / (1 + 3) = 0.25
    assert metrics["false_positive_rate"] == 0.25


def test_semantic_metrics_empty():
    from evals.metrics import compute_semantic_metrics

    metrics = compute_semantic_metrics([], [])
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1_score"] == 0.0
    assert metrics["false_positive_rate"] == 0.0


def test_compute_percentile():
    from evals.metrics import compute_percentile

    assert compute_percentile([]) == 0.0
    latencies = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    p95 = compute_percentile(latencies, 95.0)
    assert 900 <= p95 <= 1000
