import shutil
import unittest
from pathlib import Path

import pandas as pd

from earthquake_risk.data_loader import load_earthquake_data
from earthquake_risk.risk_model import enrich_events, summarize_grid_cell_risk


class RankingTests(unittest.TestCase):
    def test_higher_activity_grid_cell_ranks_above_lower_activity_grid_cell(self) -> None:
        base_dir = Path("tests/.tmp/ranking")
        base_dir.mkdir(parents=True, exist_ok=True)
        csv_path = base_dir / "sample.csv"

        try:
            csv_path.write_text(
                "time,latitude,longitude,depth,mag,place,type,id\n"
                "2023-01-01T00:00:00Z,35.1,140.1,10.0,6.0,Tokyo,earthquake,eq1\n"
                "2023-01-02T00:00:00Z,35.2,140.2,12.0,5.8,Tokyo,earthquake,eq2\n"
                "2023-01-03T00:00:00Z,38.9,145.1,90.0,4.1,Offshore,earthquake,eq3\n",
                encoding="utf-8",
            )

            loaded = load_earthquake_data(csv_path, grid_size=0.5)
            enriched = enrich_events(loaded)
            ranking = summarize_grid_cell_risk(
                enriched,
                recent_window_days=365,
                weights={
                    "event_count": 0.30,
                    "avg_magnitude": 0.25,
                    "recent_events": 0.20,
                    "shallow_ratio": 0.15,
                    "strong_event_ratio": 0.10,
                },
            )

            self.assertEqual(ranking.iloc[0]["grid_cell_key"], "35.000_140.000")
            self.assertGreater(ranking.iloc[0]["risk_score"], ranking.iloc[1]["risk_score"])
            self.assertTrue(pd.Series(ranking["risk_score"]).is_monotonic_decreasing)
        finally:
            if base_dir.exists():
                shutil.rmtree(base_dir)


if __name__ == "__main__":
    unittest.main()
