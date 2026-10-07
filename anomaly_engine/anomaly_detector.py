from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyResult:
    """Result returned by the anomaly detection engine."""

    is_anomaly: bool
    score: float
    label: str


class CloudAnomalyDetector:
    """
    Detect unusual cloud-service behavior using Isolation Forest.

   Expected features:
    1. request_count
    2. error_count
    3. average_latency_ms
    4. p95_latency_ms
    5. average_duration_ms
    6. timeout_count
    7. throttle_count
    """

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> None:
        if not 0 < contamination < 0.5:
            raise ValueError("contamination must be between 0 and 0.5")

        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )

        self._is_fitted = False

    def fit(self, training_data: Sequence[Sequence[float]]) -> None:
        """Train the detector using historical normal observations."""

        data = np.asarray(training_data, dtype=float)

        if data.ndim != 2:
            raise ValueError("training_data must be a 2D array")

        if len(data) < 10:
            raise ValueError("At least 10 observations are recommended")

        self.model.fit(data)
        self._is_fitted = True

    def predict(self, observation: Sequence[float]) -> AnomalyResult:
        """Classify an observation as NORMAL or ANOMALY."""

        if not self._is_fitted:
            raise RuntimeError("Model must be fitted before prediction")

        data = np.asarray(observation, dtype=float).reshape(1, -1)

        prediction = self.model.predict(data)[0]
        score = float(self.model.decision_function(data)[0])

        is_anomaly = prediction == -1

        return AnomalyResult(
            is_anomaly=is_anomaly,
            score=score,
            label="ANOMALY" if is_anomaly else "NORMAL",
        )