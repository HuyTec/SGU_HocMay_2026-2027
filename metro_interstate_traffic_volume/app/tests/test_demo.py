"""Meaningful inference/contract tests using artificial data, never UCI test scoring."""

import ast
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from app.src.demo import service as demo


class DemoContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = demo.audited_bundle()

    def setUp(self):
        self.hourly = demo.synthetic_hourly()
        self.at = self.hourly.date_time.iloc[192]

    def test_final_artifact_c30_order_and_three_models(self):
        features = demo.prepare_features(self.hourly, [self.at], self.bundle)
        self.assertEqual(list(features), self.bundle['features'])
        self.assertEqual(len(features.columns), 30)
        self.assertEqual(len(self.bundle['models']), 3)

    def test_timestamp_lag_across_missing_hour(self):
        missing = self.at - pd.Timedelta(hours=24)
        frame = self.hourly.loc[self.hourly.date_time.ne(missing)]
        features = demo.prepare_features(frame, [self.at], self.bundle)
        self.assertTrue(pd.isna(features.lag_24h.iloc[0]))
        self.assertTrue(pd.notna(features.mean_24h.iloc[0]))
        result = demo.infer(frame, [self.at], self.bundle, True)
        self.assertTrue(pd.isna(result.prediction.iloc[0]))

    def test_current_and_future_target_do_not_change_features_or_prediction(self):
        changed = self.hourly.copy()
        changed.loc[changed.date_time.ge(self.at), 'traffic_volume'] = 999999
        pd.testing.assert_frame_equal(demo.prepare_features(changed, [self.at], self.bundle),
                                      demo.prepare_features(self.hourly, [self.at], self.bundle))
        pd.testing.assert_frame_equal(demo.infer(changed, [self.at], self.bundle, True),
                                      demo.infer(self.hourly, [self.at], self.bundle, True))

    def test_missing_history_is_never_filled(self):
        result = demo.infer(self.hourly, [self.hourly.date_time.iloc[0]], self.bundle, True)
        self.assertTrue(pd.isna(result.prediction.iloc[0]))

    def test_adapter_and_components_match_predict_hours(self):
        expected = demo.predict_hours(self.hourly, [self.at], self.bundle)
        result, parts = demo.components(self.hourly, self.at, self.bundle, True)
        pd.testing.assert_frame_equal(result, expected)
        self.assertAlmostEqual(parts['Giá trị sau nhân trọng số'].sum(), expected.prediction.iloc[0], places=9)

    def test_external_contract_blocks_inference_and_scoring(self):
        with self.assertRaisesRegex(ValueError, 'khóa'):
            demo.infer(self.hourly, [self.at], self.bundle)
        with self.assertRaisesRegex(ValueError, 'khóa'):
            demo.evaluate_range(self.hourly, self.at, self.at, self.bundle, '2018-09-30')

    def test_scoring_intersection_and_calendar_denominator(self):
        frame = self.hourly.copy()
        frame.loc[frame.date_time.eq(self.at), 'traffic_volume'] = np.nan
        frame = frame.loc[frame.date_time.ne(self.at + pd.Timedelta(hours=1))]
        grid, counts, metrics = demo.evaluate_range(frame, self.at, self.at + pd.Timedelta(hours=3),
                                                   self.bundle, '2018-09-30', True)
        self.assertEqual(counts['Giờ kỳ vọng'], 4)
        self.assertEqual(counts['Có dự đoán'], 3)
        self.assertEqual(counts['Được chấm'], 2)
        self.assertEqual(metrics['n'], 2)
        self.assertEqual(counts['Bị loại (hợp duy nhất)'], 2)
        self.assertTrue(pd.isna(grid.loc[self.at + pd.Timedelta(hours=1), 'prediction']))
        self.assertTrue(pd.isna(grid.loc[self.at, 'absolute_error']))
        valid = grid.dropna(subset=['absolute_error'])
        self.assertAlmostEqual(metrics['MAE'], (valid.prediction - valid.traffic_volume).abs().mean())

    def test_no_pre_uci_range(self):
        with self.assertRaisesRegex(ValueError, 'sau mốc cuối UCI'):
            demo.evaluate_range(self.hourly, self.at, self.at, self.bundle, '2020-01-01', True)

    def test_history_window_excludes_t_and_has_real_sources(self):
        window = demo.history_window(self.hourly, self.at)
        self.assertEqual(len(window), 24)
        self.assertTrue(window.date_time.lt(self.at).all())
        self.assertEqual(window.date_time.min(), self.at - pd.Timedelta(hours=24))
        self.assertTrue(window.source.notna().all())

    def test_missingness_groups_overlap_without_false_ready_status(self):
        frame = self.hourly.loc[self.hourly.date_time.ne(self.at)]
        grid, counts = demo.quality_grid(frame, self.at, self.at + pd.Timedelta(hours=1))
        self.assertEqual(counts['Vắng bản ghi'], 1)
        self.assertFalse(grid.input_ready.any())
        self.assertTrue(grid.loc[self.at, 'missing_weather_raw'])

    def test_cache_token_changes_with_file_contents(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'source.csv'
            file.write_text('old')
            first = demo.file_token([file])
            file.write_text('new')
            self.assertNotEqual(first, demo.file_token([file]))

    def test_source_comparison_separates_overlap_from_new_cohort(self):
        comparison = demo.source_comparison()
        self.assertEqual(len(comparison['overlap']), 6533)
        self.assertTrue(comparison['overlap'].difference.eq(0).all())
        membership = comparison['membership'].set_index('Nhóm')['Số giờ']
        self.assertEqual(comparison['n_mndot'], 8160)
        self.assertEqual(membership['Giao timestamp UCI–MnDOT'], 6533)
        self.assertEqual(membership['Chỉ MnDOT · trong giai đoạn UCI'], 19)
        self.assertEqual(membership['Chỉ MnDOT · sau mốc cuối UCI'], 1608)
        self.assertEqual(membership.sum(), comparison['n_mndot'])
        self.assertTrue(comparison['daily_coverage'].groupby('Ngày')['Số giờ'].sum().eq(24).all())
        summary = comparison['summary'].set_index('Nguồn')
        self.assertEqual(summary.loc['MnDOT mới · sau UCI', 'Target hợp lệ'], 1608)
        self.assertEqual(summary.loc['MnDOT mới · sau UCI', 'Vắng bản ghi'], 120)
        self.assertTrue(np.allclose(comparison['histogram'].groupby('Nguồn')['Tỷ lệ (%)'].sum(), 100))
        self.assertLess(summary.loc['UCI cũ · 2018', 'Đến'], summary.loc['MnDOT mới · sau UCI', 'Từ'])

    def test_no_training_or_uci_test_entry_points_called(self):
        for path in [demo.ROOT / 'app.py', *list((demo.ROOT / 'src/demo').glob('*.py'))]:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ''
                    self.assertNotIn(name, ['fit', 'fit_final', 'evaluate_test_once'], str(path))


# The legacy source-switching UI contract is replaced by test_presentation.py.


class ReadabilityTests(unittest.TestCase):
    def test_readable_status_separates_history_contract_and_missing_actual(self):
        grid = pd.DataFrame({'has_record': [True, True, True, False],
                             'has_target': [True, True, False, False],
                             'has_history': [False, True, True, False],
                             'compatible_weather': [True, False, True, True],
                             'input_ready': [False, False, True, False],
                             'traffic_volume': [2500, 2500, np.nan, np.nan],
                             'lag_24h': [2000, 2000, 2000, np.nan],
                             'lag_168h': [np.nan, 2200, 2200, np.nan],
                             'mean_24h': [2300, 2300, 2300, np.nan]},
                            index=pd.date_range('2019-01-01', periods=4, freq='h'))
        view = demo.quality_view(grid)
        self.assertEqual(list(view['Trạng thái']), ['Thiếu lịch sử', 'Chờ xác minh nguồn',
                                                   'Có thể dự đoán', 'Không có dữ liệu giờ này'])
        self.assertIn('7 ngày', view['Giải thích'].iloc[0])
        self.assertIn('tính sai số', view['Giải thích'].iloc[2])
        uci_view = demo.quality_view(grid.iloc[[2]], 'uci')
        self.assertEqual(uci_view['Trạng thái'].iloc[0], 'Xem dữ liệu UCI')


class OpenWeatherIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.src.demo import weather
        cls.weather_module = weather
        cls.weather = weather.load()
        cls.context, cls.traffic, _, cls.end = demo.load_sources()

    def test_preview_preserves_uci_targets_calendar_and_history(self):
        w = self.weather_module
        joined = w.attach_preview(self.context, self.weather, self.end, w.POLICIES[0])
        old = self.context.date_time.le(self.end)
        pd.testing.assert_frame_equal(joined.loc[old, demo.FIELDS], self.context.loc[old, demo.FIELDS])
        for col in ['date_time', 'traffic_volume', 'is_holiday']:
            pd.testing.assert_series_equal(joined[col], self.context[col])
        for col in demo.HISTORY_FEATURES:
            pd.testing.assert_series_equal(demo.add_history_features(joined)[col],
                                           demo.add_history_features(self.context)[col])
        external = joined.loc[~old]
        self.assertEqual(len(external), 1608)
        self.assertFalse(external[w.VALUES].isna().any().any())
        self.assertTrue(external.is_holiday.isna().all())

    def test_dst_does_not_guess_repeated_or_nonexistent_hour(self):
        w = self.weather_module
        stamps = pd.to_datetime(['2018-03-11 02:00', '2018-11-04 01:00', '2018-11-04 03:00'])
        chicago = w.utc_for_wall(stamps, w.POLICIES[1])
        self.assertTrue(chicago[:2].isna().all())
        self.assertFalse(pd.isna(chicago[2]))
        self.assertFalse(w.utc_for_wall(stamps, w.POLICIES[0]).isna().any())
        joined = w.attach_preview(self.context, self.weather, self.end, w.POLICIES[1])
        external = joined.loc[joined.date_time.gt(self.end)]
        self.assertEqual(external.temp.isna().sum(), 1)

    def test_weather_comparison_matches_values_without_traffic_target(self):
        w = self.weather_module
        comparison = w.compare(demo.read_hourly(demo.UCI), self.weather, w.POLICIES[0])
        self.assertEqual(comparison['n'], 6533)
        rows = comparison['rows']
        self.assertNotIn('traffic_volume', rows)
        self.assertTrue(np.allclose(rows.temp_difference, rows.temp_ow - rows.temp_uci))
        self.assertAlmostEqual(comparison['summary'].set_index('Biến').loc['temp', 'Sai khác tuyệt đối TB'],
                               rows.temp_difference.abs().mean())


if __name__ == '__main__':
    unittest.main()
