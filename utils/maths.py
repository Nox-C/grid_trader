from __future__ import annotations

def safe_div(a: float, b: float, default: float = 0.0) -> float:
    try:
        return a / b
    except Exception:
        return default
