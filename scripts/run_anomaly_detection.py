from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split

from anomaly_engine.anomaly_detector import CloudAnomalyDetector


INPUT_FILE = Path("scripts/generated_incidents.json")

FEATURE_NAMES = [
    "request_count",
    "error_count",
    "average_latency_ms",
    "p95_latency_ms",
    "average_duration_ms",
    "timeout_count",
    "throttle_count",
]


def load_incidents() -> list[dict]:
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_features(incident: dict) -> list[float]:
    return [float(incident[name]) for name in FEATURE_NAMES]


def main() -> None:
    incidents = load_incidents()

    normal_incidents = [
        incident
        for incident in incidents
        if incident["incident_type"] == "NORMAL"
    ]

    abnormal_incidents = [
        incident
        for incident in incidents
        if incident["incident_type"] != "NORMAL"
    ]

    # 80% of NORMAL observations for training
    # 20% held out for testing
    normal_train, normal_test = train_test_split(
        normal_incidents,
        test_size=0.20,
        random_state=42,
    )

    training_data = [
        extract_features(incident)
        for incident in normal_train
    ]

    detector = CloudAnomalyDetector(
        contamination=0.05,
        random_state=42,
    )

    detector.fit(training_data)

    test_incidents = normal_test + abnormal_incidents

    y_true = []
    y_pred = []

    for incident in test_incidents:
        result = detector.predict(
            extract_features(incident)
        )

        # Ground truth:
        # 0 = normal
        # 1 = anomaly
        actual = 0 if incident["incident_type"] == "NORMAL" else 1
        predicted = 1 if result.is_anomaly else 0

        y_true.append(actual)
        y_pred.append(predicted)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    matrix = confusion_matrix(y_true, y_pred)

    print("\n=== CLOUDSENTINEL ML EVALUATION ===")
    print(f"Training normal samples: {len(normal_train)}")
    print(f"Test normal samples: {len(normal_test)}")
    print(f"Test anomaly samples: {len(abnormal_incidents)}")
    print(f"Total test samples: {len(test_incidents)}")

    print("\n=== METRICS ===")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\n=== CONFUSION MATRIX ===")
    print("[[TN  FP]")
    print(" [FN  TP]]")
    print(matrix)

    print("\n=== CLASSIFICATION REPORT ===")
    print(
        classification_report(
            y_true,
            y_pred,
            target_names=["NORMAL", "ANOMALY"],
            zero_division=0,
        )
    )


if __name__ == "__main__":
    main()