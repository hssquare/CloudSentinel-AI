from __future__ import annotations

import json
from pathlib import Path

from anomaly_engine.anomaly_detector import CloudAnomalyDetector
from incident_engine.cloudsentinel_pipeline import CloudSentinelPipeline
from incident_engine.incident_classifier import IncidentClassifier


INPUT_FILE = Path("scripts/generated_incidents.json")


def load_incidents() -> list[dict]:
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    incidents = load_incidents()

    normal_incidents = [
        incident
        for incident in incidents
        if incident["incident_type"] == "NORMAL"
    ]

    training_data = [
        CloudSentinelPipeline.extract_features(incident)
        for incident in normal_incidents
    ]

    detector = CloudAnomalyDetector(
        contamination=0.05,
        random_state=42,
    )

    detector.fit(training_data)

    classifier = IncidentClassifier()

    pipeline = CloudSentinelPipeline(
        detector=detector,
        classifier=classifier,
    )

    print("\n=== CLOUDSENTINEL END-TO-END PIPELINE ===")

    for incident in incidents[:20]:
        result = pipeline.process(incident)

        print(
            f"{incident['incident_type']:<22} → "
            f"{result['status']:<8} | "
            f"{result['incident_type']:<22} | "
            f"{result['severity']:<8} | "
            f"score={result['anomaly_score']:.4f}"
        )













if __name__ == "__main__":
    main()