import json
from pathlib import Path


DEFAULT_RISK_THRESHOLDS = {
    "low_min_ext_score": 0.65,
    "high_max_ext_score": 0.45,
}


def load_risk_thresholds(path: Path | None = None) -> dict[str, float]:
    thresholds = DEFAULT_RISK_THRESHOLDS.copy()
    if not path:
        return thresholds

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Risk threshold config must be a JSON object: {path}")

    unknown_keys = sorted(set(raw) - set(DEFAULT_RISK_THRESHOLDS))
    if unknown_keys:
        raise ValueError(f"Unknown risk threshold keys in {path}: {', '.join(unknown_keys)}")

    for key, value in raw.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"Risk threshold value for {key} must be numeric.")
        thresholds[key] = float(value)

    if thresholds["high_max_ext_score"] >= thresholds["low_min_ext_score"]:
        raise ValueError("high_max_ext_score must be lower than low_min_ext_score.")

    return thresholds
