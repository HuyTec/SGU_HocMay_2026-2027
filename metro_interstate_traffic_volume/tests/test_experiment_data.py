"""Kiểm tra hợp đồng dữ liệu và ranh giới imputation, không huấn luyện model."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.data import PROJECT_DIR, load_splits
from src.experiment_data import load_experiment_splits
from src.preprocessing import fill_weather, fit_weather_fill


class ExperimentDataTests(unittest.TestCase):
    def test_processed_preserves_snapshot_and_does_not_read_test(self):
        read_csv = pd.read_csv
        with patch("src.experiment_data.pd.read_csv", wraps=read_csv) as reader:
            actual = load_experiment_splits()
        self.assertEqual(tuple(actual), ("train", "validation"))
        self.assertFalse(any(Path(call.args[0]).name == "test.csv" for call in reader.call_args_list))
        for name, frame in actual.items():
            expected = read_csv(PROJECT_DIR / f"data/processed/{name}.csv", parse_dates=["date_time"])
            pd.testing.assert_frame_equal(frame, expected)

    def test_raw_keeps_missing_weather_for_cv(self):
        raw = load_experiment_splits(stage="raw")
        self.assertEqual((len(raw["train"]), len(raw["validation"])), (28402, 6086))
        self.assertEqual(raw["train"]["temp"].isna().sum(), 10)
        self.assertEqual(raw["train"]["rain_1h"].isna().sum(), 1)

    def test_filled_preserves_previous_preparation(self):
        current = load_experiment_splits(stage="filled")
        previous = load_splits()
        for name, frame in current.items():
            pd.testing.assert_frame_equal(frame, previous[name].reset_index(drop=True))

    def test_processed_rejects_silent_cleaning_changes(self):
        for kwargs in ({"mask_stuck_temp": True}, {"complete_holidays": True}, {"path": "another.csv"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                load_experiment_splits(**kwargs)

    def test_raw_rejects_mismatched_snapshot_target(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/processed").mkdir(parents=True)
            times = pd.date_range("2020-01-01", periods=20, freq="h")
            raw = pd.DataFrame({
                "date_time": times, "traffic_volume": np.arange(20), "holiday": "None",
                "temp": 280.0, "rain_1h": 0.0, "snow_1h": 0.0, "clouds_all": 0,
                "weather_main": "Clear", "weather_description": "sky is clear",
            })
            source = root / "data/Metro_Interstate_Traffic_Volume.csv"
            raw.to_csv(source, index=False)
            for name, bounds in {"train": (0, 14), "validation": (14, 17)}.items():
                frame = raw.iloc[slice(*bounds)][["date_time", "traffic_volume"]].copy()
                if name == "validation":
                    frame.iloc[0, frame.columns.get_loc("traffic_volume")] = 999
                frame.to_csv(root / f"data/processed/{name}.csv", index=False)
            with self.assertRaisesRegex(ValueError, "timestamp/target"):
                load_experiment_splits(project_dir=root, stage="raw")

    def test_missing_snapshot_does_not_fall_back_to_raw(self):
        with TemporaryDirectory() as directory, self.assertRaisesRegex(FileNotFoundError, "snapshot"):
            load_experiment_splits(project_dir=directory, stage="raw")

    def test_cv_recomputes_imputation_without_later_fold_statistics(self):
        # First missing hour has no past reading. Later hours must not set its
        # fallback median in the first CV fold.
        from src.tuning import _prepare_folds

        raw = pd.DataFrame({
            "date_time": pd.date_range("2020-01-01", periods=8, freq="h"),
            "traffic_volume": np.arange(8),
            "temp": [np.nan, 280.0, 320.0, 320.0, 320.0, 320.0, 320.0, 320.0],
            "rain_1h": 0.0,
        })
        prepared = fill_weather(raw, fit_weather_fill(raw))
        prepared["temp_c"] = prepared["temp"] - 273.15
        folds = _prepare_folds(prepared, ["temp_c"], raw)
        self.assertAlmostEqual(prepared.iloc[0]["temp_c"], 320.0 - 273.15)
        self.assertAlmostEqual(folds[0][0].iloc[0]["temp_c"], 280.0 - 273.15)


if __name__ == "__main__":
    unittest.main()
