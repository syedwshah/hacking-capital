def test_health_route(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_agent_weights_normalization(client):
    # Test that weights are normalized to sum to 1.0
    weights_payload = [
        {"agent": "primary", "weight": 0.5},
        {"agent": "investor_patterns", "weight": 0.3},
        {"agent": "sentiment_tailwinds", "weight": 0.2},
        {"agent": "vector_similarity", "weight": 0.1}
    ]

    r = client.post("/api/v1/agents/weights", json={"weights": weights_payload})
    assert r.status_code == 200
    result = r.json()
    assert result["ok"] is True

    normalized_weights = result["weights"]
    total_weight = sum(w["weight"] for w in normalized_weights)
    assert abs(total_weight - 1.0) < 0.001  # Should sum to approximately 1.0

    # Verify we can retrieve the weights
    r_get = client.get("/api/v1/agents/weights")
    assert r_get.status_code == 200
    retrieved = r_get.json()["weights"]
    assert len(retrieved) == len(normalized_weights)


