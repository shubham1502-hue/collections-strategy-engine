from pathlib import Path
import importlib.util
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from risk_config import load_risk_thresholds


def load_profile_module():
    module_path = ROOT / "src" / "01_load_and_profile.py"
    spec = importlib.util.spec_from_file_location("load_and_profile", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_custom_risk_threshold_changes_segment_assignment():
    module = load_profile_module()
    df = pd.DataFrame({"ext_score_avg": [0.62, 0.50, 0.43]})
    thresholds = {"low_min_ext_score": 0.60, "high_max_ext_score": 0.45}

    segmented = module.assign_risk_tier(df, thresholds)

    assert segmented["risk_tier"].tolist() == ["Low", "Medium", "High"]


def test_example_bnpl_config_loads():
    thresholds = load_risk_thresholds(ROOT / "configs" / "bnpl-risk-segments.json")

    assert thresholds["low_min_ext_score"] == 0.62
    assert thresholds["high_max_ext_score"] == 0.42
