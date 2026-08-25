from __future__ import annotations

import json
from pathlib import Path

import joblib

from anomaly_engine.anomaly_detector import CloudAnomalyDetector
from incident_engine.cloudsentinel_pipeline import CloudSentinelPipeline


DATA_FILE = Path("scripts/generated_incidents.json")
MODEL_FILE = Path("models/anomaly_detector.joblib")


def load_normal_training_data() -> list[list[float]]:
    """Load normal telemetry and convert it into model features."""

    with DATA_FILE.open("r", encoding="utf-8") as file:
        incidents = json.load(file)

    normal_incidents = [
        incident
        for incident in incidents
        if incident["incident_type"] == "NORMAL"
    ]

    if len(normal_incidents) < 10:
        raise ValueError("At least 10 normal observations are required.")

    return [
        list(
            CloudSentinelPipeline.extract_features(incident)
        )
        for incident in normal_incidents
    ]


def main() -> None:
    training_data = load_normal_training_data()

    detector = CloudAnomalyDetector(
        contamination=0.05,
        random_state=42,
    )

    detector.fit(training_data)

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(detector, MODEL_FILE)

    print("=== MODEL TRAINING COMPLETE ===")
    print(f"Training samples: {len(training_data)}")
    print(f"Model saved to: {MODEL_FILE}")


if __name__ == "__main__":
    main()