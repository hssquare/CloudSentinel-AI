from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Structured result returned by the incident classifier."""

    incident_type: str
    severity: str
    reason: str


class IncidentClassifier:
    """
    Rule-based incident classifier.

    Input:
        Cloud telemetry metrics.

    Output:
        Incident type, severity, and explanation.
    """

    def classify(self, incident: dict) -> ClassificationResult:

        # NORMAL telemetry
        if incident.get("incident_type") == "NORMAL":
            return ClassificationResult(
                incident_type="NORMAL",
                severity="NONE",
                reason="Telemetry is within the normal operating baseline.",
            )

        timeout_count = incident.get("timeout_count", 0)
        throttle_count = incident.get("throttle_count", 0)
        error_count = incident.get("error_count", 0)

        latency = incident.get("average_latency_ms", 0)
        p95_latency = incident.get("p95_latency_ms", 0)
        duration = incident.get("average_duration_ms", 0)
        request_count = incident.get("request_count", 0)

        # Calculate error rate for stronger classification.
        error_rate = (
            error_count / request_count
            if request_count > 0
            else 0
        )

        # ---------------------------------------------------------
        # 1. DynamoDB throttling
        # ---------------------------------------------------------
        if throttle_count >= 15:
            return ClassificationResult(
                incident_type="DYNAMODB_THROTTLING",
                severity="HIGH",
                reason="Repeated throttling events detected.",
            )

        # ---------------------------------------------------------
        # 2. HTTP 5xx spike
        # ---------------------------------------------------------
        if (
            error_count >= 80
            and error_rate >= 0.20
        ):
            return ClassificationResult(
                incident_type="HTTP_5XX_SPIKE",
                severity="CRITICAL",
                reason=(
                    "A large proportion of requests returned errors, "
                    "indicating a significant HTTP 5xx spike."
                ),
            )

        # ---------------------------------------------------------
        # 3. Lambda timeout
        # ---------------------------------------------------------
        if (
            timeout_count >= 15
            and duration >= 5000
            and p95_latency >= 5000
        ):
            return ClassificationResult(
                incident_type="LAMBDA_TIMEOUT",
                severity="HIGH",
                reason=(
                    "High timeout frequency combined with long "
                    "execution duration indicates Lambda timeouts."
                ),
            )

        # ---------------------------------------------------------
        # 4. S3 access denied
        # ---------------------------------------------------------
        if (
            error_count >= 15
            and latency < 500
            and timeout_count == 0
            and throttle_count == 0
        ):
            return ClassificationResult(
                incident_type="S3_ACCESS_DENIED",
                severity="MEDIUM",
                reason=(
                    "High error count with low latency and no "
                    "timeouts or throttling suggests access failures."
                ),
            )

        # ---------------------------------------------------------
        # 5. High latency
        # ---------------------------------------------------------
        if (
            latency >= 1000
            or p95_latency >= 2000
        ):
            return ClassificationResult(
                incident_type="HIGH_LATENCY",
                severity="MEDIUM",
                reason=(
                    "Application latency exceeded the normal "
                    "operating threshold."
                ),
            )

        # ---------------------------------------------------------
        # 6. Unknown
        # ---------------------------------------------------------
        return ClassificationResult(
            incident_type="UNKNOWN",
            severity="LOW",
            reason="No known incident pattern matched.",




        )