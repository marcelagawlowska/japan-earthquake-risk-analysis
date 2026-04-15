import shutil
import unittest
from pathlib import Path

from earthquake_risk.data_loader import load_earthquake_data


class DataLoaderTests(unittest.TestCase):
    def test_load_earthquake_data_rejects_non_positive_grid_size(self) -> None:
        base_dir = Path("tests/.tmp/data_loader")
        base_dir.mkdir(parents=True, exist_ok=True)
        csv_path = base_dir / "sample.csv"

        try:
            csv_path.write_text(
                "time,latitude,longitude,depth,mag,place,type,id\n"
                "2023-01-01T00:00:00Z,35.0,140.0,10.0,5.0,Tokyo,earthquake,abc\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_earthquake_data(csv_path, grid_size=0)
        finally:
            if base_dir.exists():
                shutil.rmtree(base_dir)


if __name__ == "__main__":
    unittest.main()
