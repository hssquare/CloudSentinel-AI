from __future__ import annotations

import json
from pathlib import Path

from incident_engine.incident_classifier import IncidentClassifier


INPUT_FILE = Path("scripts/generated_incidents.json")


def load_incidents() -> list[dict]:
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    incidents = load_incidents()
    classifier = IncidentClassifier()

    print("\n=== CLOUDSENTINEL INCIDENT CLASSIFICATION ===")

    for incident in incidents[:20]:
        result = classifier.classify(incident)

        print(
            f"{incident['incident_type']:<22} "
            f"→ {result.incident_type:<22} "
            f"| severity={result.severity:<8} "
            f"| {result.reason}"
        )


if __name__ == "__main__":
    main()