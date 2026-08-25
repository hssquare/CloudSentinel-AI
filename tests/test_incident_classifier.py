from __future__ import annotations

import json
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from incident_engine.incident_classifier import IncidentClassifier


INPUT_FILE = Path("scripts/generated_incidents.json")


def main() -> None:
    """Evaluate the incident classifier on the synthetic dataset."""

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        incidents = json.load(file)

    classifier = IncidentClassifier()

    y_true = []
    y_pred = []

    for incident in incidents:
        result = classifier.classify(incident)

        y_true.append(incident["incident_type"])
        y_pred.append(result.incident_type)

    labels = sorted(set(y_true))

    accuracy = accuracy_score(y_true, y_pred)

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    print("\n=== INCIDENT CLASSIFIER EVALUATION ===")
    print(f"Total samples: {len(incidents)}")
    print(f"Accuracy: {accuracy:.4f}")

    print("\n=== LABELS ===")
    print(labels)

    print("\n=== CONFUSION MATRIX ===")
    print(matrix)

    print("\n=== CLASSIFICATION REPORT ===")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
        )
    )








if __name__ == "__main__":
    main()