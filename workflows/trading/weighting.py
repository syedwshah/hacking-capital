def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(v)) for v in weights.values()) or 1.0
    return {k: max(0.0, float(v)) / total for k, v in weights.items()}


