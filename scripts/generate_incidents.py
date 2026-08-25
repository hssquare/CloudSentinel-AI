from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_FILE = Path("scripts/generated_incidents.json")


def create_incident(incident_type: str) -> dict:
    """Generate a realistic synthetic cloud incident."""

    timestamp = datetime.now(timezone.utc).isoformat()

    base = {
        "timestamp": timestamp,
        "application": "cloudsentinel-demo-app",
        "service": "image-processing-service",
        "region": "ap-south-1",
    }

    if incident_type == "NORMAL":
        return {
            **base,
            "incident_type": "NORMAL",
            "request_count": random.randint(90, 130),
            "error_count": random.randint(0, 4),
            "average_latency_ms": random.randint(100, 180),
            "p95_latency_ms": random.randint(160, 250),
            "average_duration_ms": random.randint(150, 250),
            "timeout_count": 0,
            "throttle_count": 0,
        }

    if incident_type == "HIGH_LATENCY":
        return {
            **base,
            "incident_type": "HIGH_LATENCY",
            "request_count": random.randint(90, 140),
            "error_count": random.randint(5, 15),
            "average_latency_ms": random.randint(1200, 3000),
            "p95_latency_ms": random.randint(2500, 5000),
            "average_duration_ms": random.randint(900, 2500),
            "timeout_count": random.randint(1, 5),
            "throttle_count": 0,
        }

    if incident_type == "LAMBDA_TIMEOUT":
        return {
            **base,
            "incident_type": "LAMBDA_TIMEOUT",
            "request_count": random.randint(250, 600),
            "error_count": random.randint(40, 100),
            "average_latency_ms": random.randint(3000, 6000),
            "p95_latency_ms": random.randint(6000, 10000),
            "average_duration_ms": random.randint(5000, 9000),
            "timeout_count": random.randint(15, 40),
            "throttle_count": 0,
        }

    if incident_type == "DYNAMODB_THROTTLING":
        return {
            **base,
            "incident_type": "DYNAMODB_THROTTLING",
            "request_count": random.randint(400, 800),
            "error_count": random.randint(30, 90),
            "average_latency_ms": random.randint(500, 1800),
            "p95_latency_ms": random.randint(1500, 4000),
            "average_duration_ms": random.randint(500, 2000),
            "timeout_count": random.randint(2, 10),
            "throttle_count": random.randint(20, 60),
        }

    if incident_type == "S3_ACCESS_DENIED":
        return {
            **base,
            "incident_type": "S3_ACCESS_DENIED",
            "request_count": random.randint(100, 250),
            "error_count": random.randint(20, 60),
            "average_latency_ms": random.randint(150, 400),
            "p95_latency_ms": random.randint(300, 700),
            "average_duration_ms": random.randint(150, 450),
            "timeout_count": 0,
            "throttle_count": 0,
        }

    if incident_type == "HTTP_5XX_SPIKE":
        return {
            **base,
            "incident_type": "HTTP_5XX_SPIKE",
            "request_count": random.randint(500, 1000),
            "error_count": random.randint(100, 300),
            "average_latency_ms": random.randint(400, 1500),
            "p95_latency_ms": random.randint(1200, 3000),
            "average_duration_ms": random.randint(400, 1500),
            "timeout_count": random.randint(5, 20),
            "throttle_count": 0,
        }

    raise ValueError(f"Unsupported incident type: {incident_type}")


def generate_dataset(count_per_type: int = 10) -> list[dict]:
    """Generate a balanced synthetic incident dataset."""

    incident_types = [
        "NORMAL",
        "HIGH_LATENCY",
        "LAMBDA_TIMEOUT",
        "DYNAMODB_THROTTLING",
        "S3_ACCESS_DENIED",
        "HTTP_5XX_SPIKE",
    ]

    incidents: list[dict] = []

    for incident_type in incident_types:
        for _ in range(count_per_type):
            incidents.append(create_incident(incident_type))

    random.shuffle(incidents)

    return incidents


def save_dataset(incidents: list[dict]) -> None:
    """Save incidents as formatted JSON."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(incidents, file, indent=2)

    print(f"Generated {len(incidents)} incidents.")
    print(f"Saved to: {OUTPUT_FILE}")


def main() -> None:
    incidents = generate_dataset(count_per_type=100)
    save_dataset(incidents)

if __name__ == "__main__":
    main()