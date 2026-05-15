from pathlib import Path
import importlib.util
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "02_offer_logic.py"

spec = importlib.util.spec_from_file_location("offer_logic", MODULE_PATH)
offer_logic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(offer_logic)


class ChannelExampleTests(unittest.TestCase):
    def test_assign_offers_adds_channel_action_fields(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "dpd_bucket": "DPD_31_60",
                    "risk_tier": "High",
                    "AMT_CREDIT": 1000,
                    "preferred_channel": "SMS",
                    "optimal_contact_window": "Morning",
                },
                {
                    "dpd_bucket": "Current",
                    "risk_tier": "Low",
                    "AMT_CREDIT": 1000,
                    "preferred_channel": "SMS",
                    "optimal_contact_window": "Afternoon",
                },
            ]
        )

        result = offer_logic.assign_offers(df)

        expected_fields = {
            "primary_message_channel",
            "message_timing",
            "whatsapp_action",
            "sms_action",
            "primary_channel_action",
        }
        self.assertTrue(expected_fields.issubset(result.columns))
        self.assertEqual(result.loc[0, "primary_message_channel"], "WHATSAPP")
        self.assertIn("repayment link", result.loc[0, "primary_channel_action"])
        self.assertEqual(result.loc[1, "primary_message_channel"], "SMS")
        self.assertEqual(result.loc[1, "primary_channel_action"], result.loc[1, "sms_action"])


if __name__ == "__main__":
    unittest.main()
