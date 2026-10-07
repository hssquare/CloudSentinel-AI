from anomaly_engine.anomaly_detector import CloudAnomalyDetector


def main() -> None:
    # Features:
    # [request_count,
    #  error_count,
    #  average_latency_ms,
    #  p95_latency_ms,
    #  average_duration_ms,
    #  timeout_count,
    #  throttle_count]

    training_data = [
        [100, 2, 120, 200, 180, 0, 0],
        [105, 3, 125, 210, 185, 0, 0],
        [98, 1, 115, 190, 175, 0, 0],
        [110, 2, 130, 220, 190, 0, 0],
        [102, 2, 122, 205, 182, 0, 0],
        [108, 3, 128, 215, 188, 0, 0],
        [95, 1, 110, 185, 170, 0, 0],
        [115, 3, 135, 225, 195, 0, 0],
        [101, 2, 121, 200, 181, 0, 0],
        [107, 2, 127, 212, 187, 0, 0],
        [99, 1, 118, 195, 178, 0, 0],
        [104, 2, 124, 208, 184, 0, 0],
    ]

    detector = CloudAnomalyDetector(
        contamination=0.10,
        random_state=42,
    )

    detector.fit(training_data)

    normal_observation = [103, 2, 123, 205, 183, 0, 0]

    anomalous_observation = [
        500,
        80,
        5000,
        8000,
        7000,
        30,
        25,
    ]

    normal_result = detector.predict(normal_observation)
    anomaly_result = detector.predict(anomalous_observation)

    print("=== NORMAL TEST ===")
    print(normal_result)

    print("\n=== ANOMALY TEST ===")
    print(anomaly_result)


if __name__ == "__main__":
    main()