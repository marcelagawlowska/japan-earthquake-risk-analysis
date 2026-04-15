import shutil
import unittest
from pathlib import Path

from earthquake_risk.pipeline import run_analysis


class PipelineTests(unittest.TestCase):
    def test_run_analysis_rejects_non_positive_recent_window(self) -> None:
        with self.assertRaises(ValueError):
            run_analysis(recent_window_days=0)

    def test_run_analysis_rejects_non_positive_top_cells(self) -> None:
        with self.assertRaises(ValueError):
            run_analysis(top_cells=0)

    def test_run_analysis_creates_summary_for_small_dataset(self) -> None:
        base_dir = Path("tests/.tmp/pipeline")
        base_dir.mkdir(parents=True, exist_ok=True)
        csv_path = base_dir / "sample.csv"
        output_dir = base_dir / "outputs"

        try:
            csv_path.write_text(
                "time,latitude,longitude,depth,mag,place,type,id\n"
                "2023-01-01T00:00:00Z,35.1,140.1,10.0,5.2,Tokyo,earthquake,eq1\n"
                "2023-02-01T00:00:00Z,35.3,140.2,25.0,6.1,Tokyo,earthquake,eq2\n",
                encoding="utf-8",
            )

            summary = run_analysis(
                data_file=csv_path,
                output_dir=output_dir,
                grid_size=0.5,
                recent_window_days=365,
                top_cells=1,
            )

            self.assertEqual(summary["records"], 2)
            self.assertEqual(len(summary["top_risk_grid_cells"]), 1)
            self.assertTrue((output_dir / "analysis_summary.json").exists())
            self.assertTrue((output_dir / "grid_cell_risk_summary.csv").exists())
            self.assertTrue((output_dir / "analysis_report.md").exists())
            self.assertTrue((output_dir / "alert_distribution.svg").exists())
            self.assertTrue((output_dir / "monthly_activity.svg").exists())
            self.assertEqual(summary["top_risk_grid_cells"][0]["risk_rank"], 1)
        finally:
            if base_dir.exists():
                shutil.rmtree(base_dir)


if __name__ == "__main__":
    unittest.main()
