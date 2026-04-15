import unittest

import pandas as pd

from earthquake_risk.risk_model import (
    classify_event_alert,
    classify_risk_level,
    enrich_events,
    validate_risk_weights,
)


class RiskModelTests(unittest.TestCase):
    def test_classify_event_alert_uses_expected_thresholds(self) -> None:
        self.assertEqual(classify_event_alert(7.2), "CRITICAL")
        self.assertEqual(classify_event_alert(6.3), "HIGH")
        self.assertEqual(classify_event_alert(5.4), "MEDIUM")
        self.assertEqual(classify_event_alert(4.4), "LOW")

    def test_classify_risk_level_uses_expected_thresholds(self) -> None:
        self.assertEqual(classify_risk_level(0.80), "CRITICAL")
        self.assertEqual(classify_risk_level(0.60), "HIGH")
        self.assertEqual(classify_risk_level(0.40), "MEDIUM")
        self.assertEqual(classify_risk_level(0.20), "LOW")

    def test_enrich_events_adds_flags_and_priority(self) -> None:
        frame = pd.DataFrame(
            [
                {"mag": 7.1, "depth": 20},
                {"mag": 4.9, "depth": 120},
            ]
        )

        enriched = enrich_events(frame)

        self.assertListEqual(enriched["alert_level"].tolist(), ["CRITICAL", "LOW"])
        self.assertListEqual(enriched["priority"].tolist(), [4, 1])
        self.assertListEqual(enriched["is_strong"].tolist(), [True, False])
        self.assertListEqual(enriched["is_shallow"].tolist(), [True, False])

    def test_validate_risk_weights_requires_complete_weight_map(self) -> None:
        with self.assertRaises(ValueError):
            validate_risk_weights({"event_count": 1.0})

    def test_validate_risk_weights_requires_sum_of_one(self) -> None:
        weights = {
            "event_count": 0.2,
            "avg_magnitude": 0.2,
            "recent_events": 0.2,
            "shallow_ratio": 0.2,
            "strong_event_ratio": 0.3,
        }

        with self.assertRaises(ValueError):
            validate_risk_weights(weights)


if __name__ == "__main__":
    unittest.main()
