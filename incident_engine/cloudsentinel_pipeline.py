from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

from anomaly_engine.anomaly_detector import CloudAnomalyDetector
from incident_engine.incident_classifier import IncidentClassifier


@dataclass
class PipelineResult:
    """Structured result produced by the CloudSentinel pipeline."""

    status: str
    incident_type: str
    severity: str
    reason: str
    confidence: float
    anomaly_score: float


class CloudSentinelPipeline:
    """
    End-to-end local CloudSentinel intelligence pipeline.

    Flow:
        Telemetry
            ↓
        Anomaly Detection
            ↓
        NORMAL / ANOMALY
            ↓
        Incident Classification
            ↓
        Structured Incident Result
    """

    def __init__(
        self,
        detector: CloudAnomalyDetector,
        classifier: IncidentClassifier,
    ) -> None:
        self.detector = detector
        self.classifier = classifier

    @staticmethod
    def extract_features(incident: dict) -> Sequence[float]:
        """Extract telemetry features used by the anomaly detector."""

        return [
            float(incident["request_count"]),
            float(incident["error_count"]),
            float(incident["average_latency_ms"]),
            float(incident["p95_latency_ms"]),
            float(incident["average_duration_ms"]),
            float(incident["timeout_count"]),
            float(incident["throttle_count"]),
        ]

    def process(self, incident: dict) -> dict:
        """
        Analyze one telemetry record and return a structured result.
        """

        anomaly_result = self.detector.predict(
            self.extract_features(incident)
        )

        # ---------------------------------------------------------
        # NORMAL TELEMETRY
        # ---------------------------------------------------------
        if not anomaly_result.is_anomaly:
            result = PipelineResult(
                status="NORMAL",
                incident_type="NORMAL",
                severity="NONE",
                reason="Telemetry is within the learned normal baseline.",
                confidence=1.0,
                anomaly_score=anomaly_result.score,
            )

            return asdict(result)

        # ---------------------------------------------------------
        # ANOMALOUS TELEMETRY
        # ---------------------------------------------------------
        classification = self.classifier.classify(incident)

        result = PipelineResult(
            status="ANOMALY",
            incident_type=classification.incident_type,
            severity=classification.severity,
            reason=classification.reason,
            confidence=classification.confidence,
            anomaly_score=anomaly_result.score,
        )

        return asdict(result)