def summary_key(symbol: str, granularity: str) -> str:
    return f"kc:v1:sym:{symbol}:g:{granularity}"


TTL_SECONDS = {
    "minute": 300,
    "hour": 7200,
    "daily": 86400,
    "weekly": 604800,
}


