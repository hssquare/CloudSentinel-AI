from anomaly_engine.anomaly_detector import CloudAnomalyDetector


def main() -> None:
    # [request_count, error_count, latency_ms, duration_ms]

    training_data = [
        [100, 2, 120, 180],
        [105, 3, 125, 185],
        [98, 1, 115, 175],
        [110, 2, 130, 190],
        [102, 2, 122, 182],
        [108, 3, 128, 188],
        [95, 1, 110, 170],
        [115, 3, 135, 195],
        [101, 2, 121, 181],
        [107, 2, 127, 187],
        [99, 1, 118, 178],
        [104, 2, 124, 184],
    ]

    detector = CloudAnomalyDetector(
        contamination=0.10,
        random_state=42,
    )

    detector.fit(training_data)

    normal_observation = [103, 2, 123, 183]
    anomalous_observation = [500, 80, 5000, 7000]

    normal_result = detector.predict(normal_observation)
    anomaly_result = detector.predict(anomalous_observation)

    print("=== NORMAL TEST ===")
    print(normal_result)

    print("\n=== ANOMALY TEST ===")
    print(anomaly_result)


if __name__ == "__main__":
    main()