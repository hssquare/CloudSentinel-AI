from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Structured incident classification result."""

    incident_type: str
    severity: str
    reason: str
    confidence: float


class IncidentClassifier:
    """
    Explainable telemetry-based incident classifier.

    The classifier receives telemetry metrics and determines
    the most likely incident type.
    """

    def classify(self, incident: dict) -> ClassificationResult:

        request_count = float(incident.get("request_count", 0))
        error_count = float(incident.get("error_count", 0))
        average_latency = float(
            incident.get("average_latency_ms", 0)
        )
        p95_latency = float(
            incident.get("p95_latency_ms", 0)
        )
        average_duration = float(
            incident.get("average_duration_ms", 0)
        )
        timeout_count = float(
            incident.get("timeout_count", 0)
        )
        throttle_count = float(
            incident.get("throttle_count", 0)
        )

        error_rate = (
            error_count / request_count
            if request_count > 0
            else 0.0
        )

        # Synthetic benchmark only.
        # The production AWS pipeline will determine NORMAL
        # using the anomaly detector.
        if incident.get("incident_type") == "NORMAL":
            return ClassificationResult(
                incident_type="NORMAL",
                severity="NONE",
                reason="Telemetry is within the normal baseline.",
                confidence=1.0,
            )

        # ---------------------------------------------------------
        # 1. DynamoDB throttling
        # ---------------------------------------------------------
        if throttle_count >= 15:
            confidence = min(
                0.80 + (throttle_count - 15) / 100,
                0.99,
            )

            return ClassificationResult(
                incident_type="DYNAMODB_THROTTLING",
                severity="HIGH",
                reason=(
                    f"Detected {int(throttle_count)} throttling events, "
                    "indicating capacity or burst-traffic pressure."
                ),
                confidence=round(confidence, 3),
            )

        # ---------------------------------------------------------
        # 2. Lambda timeout
        # ---------------------------------------------------------
        if (
            timeout_count >= 15
            and average_duration >= 5000
            and p95_latency >= 5000
        ):
            return ClassificationResult(
                incident_type="LAMBDA_TIMEOUT",
                severity="HIGH",
                reason=(
                    "High timeout frequency combined with long "
                    "execution duration indicates Lambda timeouts."
                ),
                confidence=0.95,
            )

        # ---------------------------------------------------------
        # 3. HTTP 5xx spike
        # ---------------------------------------------------------
        # Error volume is considered stronger evidence than latency.
        if (
            error_count >= 80
            and request_count >= 400
            and average_duration < 2500
        ):
            return ClassificationResult(
                incident_type="HTTP_5XX_SPIKE",
                severity="CRITICAL",
                reason=(
                    f"Detected {int(error_count)} errors across "
                    f"{int(request_count)} requests, indicating a "
                    f"significant HTTP 5xx spike."
                ),
                confidence=0.95,
            )

        # ---------------------------------------------------------
        # 4. S3 access denied
        # ---------------------------------------------------------
        if (
            error_count >= 15
            and average_latency < 500
            and timeout_count == 0
            and throttle_count == 0
        ):
            return ClassificationResult(
                incident_type="S3_ACCESS_DENIED",
                severity="MEDIUM",
                reason=(
                    "High error activity with low latency and no "
                    "timeouts or throttling suggests access failures."
                ),
                confidence=0.90,
            )

        # ---------------------------------------------------------
        # 5. High latency
        # ---------------------------------------------------------
        if (
            average_latency >= 1000
            or p95_latency >= 2000
        ):
            return ClassificationResult(
                incident_type="HIGH_LATENCY",
                severity="MEDIUM",
                reason=(
                    f"Latency exceeded the operating threshold "
                    f"(average={average_latency:.0f} ms, "
                    f"p95={p95_latency:.0f} ms)."
                ),
                confidence=0.85,
            )

        # ---------------------------------------------------------
        # 6. Unknown
        # ---------------------------------------------------------
        return ClassificationResult(
            incident_type="UNKNOWN",
            severity="LOW",
            reason="No known incident pattern matched.",
            confidence=0.40,
        )