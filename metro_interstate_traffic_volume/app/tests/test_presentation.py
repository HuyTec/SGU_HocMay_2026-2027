"""Read-only numerical and UI acceptance tests for the UCI-first presentation."""
from pathlib import Path
import json
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from app.src.demo import service as d, presentation as v, presentation_charts as c


class PresentationEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.hourly = d.load_uci_sources()
        cls.saved, cls.report, cls.measured = v.verified_results()
        cls.at = cls.saved.loc[cls.saved.prediction.notna(), 'date_time'].iloc[0]
        cls.bundle = d.audited_bundle()

    def test_saved_metrics_and_scope_denominators_match_report(self):
        self.assertEqual(self.measured['n'], 6052)
        self.assertEqual(self.measured['n_total'], 6087)
        for key in ['MAE', 'RMSE', 'R2']:
            self.assertAlmostEqual(self.measured[key], self.report['metrics'][key], places=9)
        scope = self.saved.iloc[:48]
        summary = v.metrics(scope)
        self.assertEqual(summary['n_total'], 48)
        self.assertAlmostEqual(summary['MAE'], (scope.prediction-scope.actual).abs().mean())

    def test_calculation_trace_tree_paths_and_boosting_are_real(self):
        from app.src.demo import calculation
        trace = calculation.run(self.hourly, self.at, self.saved, self.bundle)
        self.assertAlmostEqual(trace['prediction'], self.saved.prediction.iloc[0], places=5)
        self.assertEqual(len(trace['parts']), 3)
        self.assertTrue(trace['parts']['Thời gian (ms)'].ge(0).all())
        np.testing.assert_allclose(trace['parts']['Sau nhân trọng số'],
                                   trace['parts']['Sau clip ≥ 0'] * trace['parts']['Trọng số'])
        for name in ['Random Forest', 'ExtraTrees']:
            path, value = calculation.tree_path(trace['features'], self.bundle, name, 0)
            self.assertEqual(path['Đặc trưng'].iloc[-1], 'Lá kết thúc')
            self.assertAlmostEqual(path['Giá trị tại nút/lá'].iloc[-1], value)
            self.assertEqual(path['Nút kế tiếp'].iloc[:-1].astype(int).tolist(), path['Nút'].iloc[1:].tolist())
        curve = calculation.boosting_curve(trace['features'], self.bundle)
        self.assertEqual(len(curve), self.bundle['models']['XGBoost'].get_booster().num_boosted_rounds())
        expected = trace['parts'].set_index('Mô hình').loc['XGBoost','Dự đoán gốc']
        self.assertAlmostEqual(curve['Dự đoán XGBoost'].iloc[-1], expected, places=5)
        figure = c.calculation_animation(trace)
        self.assertIn('Chưa mở', figure.frames[0].data[0].text[-1])
        self.assertIn('Actual', figure.frames[-1].data[0].text[-1])
        changed = self.hourly.copy()
        changed.loc[changed.date_time.ge(self.at),'traffic_volume'] = 9999999
        self.assertEqual(calculation.run(changed,self.at,self.saved,self.bundle)['prediction'],trace['prediction'])

    def test_calculation_missing_history_stops_before_models(self):
        from app.src.demo import calculation
        frame = self.hourly.loc[self.hourly.date_time.ne(self.at-pd.Timedelta(hours=168))]
        with patch.object(self.bundle['models']['Random Forest'], 'predict', side_effect=AssertionError('must not infer')):
            with self.assertRaisesRegex(ValueError, '30 đầu vào'):
                calculation.run(frame,self.at,self.saved,self.bundle)

    def test_walkthrough_uses_real_shared_preprocessing(self):
        before, after = v.duplicate_example(self.raw, self.hourly)
        self.assertGreater(len(before), 1)
        self.assertEqual(len(after), 1)
        self.assertEqual(after.traffic_volume.iloc[0], before.traffic_volume.iloc[0])
        for case in ['temp', 'rain']:
            before, after = v.cleaning_example(self.raw, self.hourly, case)
            col = 'temp' if case == 'temp' else 'rain_1h'
            self.assertTrue(after[col].isna().all())
        summary = v.split_summary(self.hourly).set_index('Tập')
        self.assertEqual(summary.loc['train', 'Số giờ quan sát'], 28402)
        self.assertEqual(summary.loc['test', 'Đủ history'], 6052)

    def test_history_highlights_and_vector_exclude_current_and_future_targets(self):
        for name, offset in [('lag_24h', 24), ('lag_168h', 168)]:
            cells = v.history_cells(self.hourly, self.at, name)
            self.assertEqual(cells.loc[cells.in_window, 'date_time'].tolist(), [self.at-pd.Timedelta(hours=offset)])
            self.assertFalse(cells.loc[cells.is_current, 'is_used'].any())
        cells = v.history_cells(self.hourly, self.at, 'mean_24h')
        self.assertEqual(int(cells.in_window.sum()), 24)
        self.assertTrue(cells.loc[cells.is_used, 'date_time'].lt(self.at).all())
        frame = v.inspected_features(self.hourly, self.at, self.bundle)
        self.assertAlmostEqual(frame.mean_24h.iloc[0], cells.loc[cells.is_used, 'traffic_volume'].mean(), places=3)
        changed = self.hourly.copy()
        changed.loc[changed.date_time.ge(self.at), 'traffic_volume'] = 9999999
        pd.testing.assert_frame_equal(frame, v.inspected_features(changed, self.at, self.bundle))
        self.assertEqual(list(frame), self.bundle['features'])
        self.assertTrue((frame.dtypes == 'float32').all())

    def test_stored_never_invokes_model_and_live_single_hour_matches(self):
        with patch.object(d, 'components', side_effect=AssertionError('stored must not infer')):
            result, parts = v.one_hour(self.hourly, self.at, self.saved)
        self.assertTrue(parts.empty)
        self.assertEqual(result['prediction'], self.saved.prediction.iloc[0])
        live, parts = v.one_hour(self.hourly, self.at, self.saved, self.bundle, 'live')
        self.assertAlmostEqual(live['prediction'], result['prediction'], places=5)
        self.assertEqual(len(parts), 3)
        self.assertAlmostEqual(parts['Giá trị sau nhân trọng số'].sum(), live['prediction'], places=8)
        with self.assertRaisesRegex(ValueError, 'artifact'):
            v.one_hour(self.hourly, self.at, self.saved, None, 'live')

    def test_frames_pause_and_linked_rectangles_have_actual_timestamps(self):
        result, _ = v.one_hour(self.hourly, self.at, self.saved)
        figure = c.prediction_animation(result)
        self.assertEqual(len(figure.frames), 5)
        self.assertEqual(figure.layout.updatemenus[0].buttons[1].label, 'Dừng')
        self.assertIn(f"{result['prediction']:.2f}", figure.data[0].text[2])
        history = c.history_timeline(v.history_cells(self.hourly, self.at, 'lag_168h'))
        self.assertEqual(history.data[0].customdata[0][0], str(self.at-pd.Timedelta(hours=168)))
        errors = c.linked_errors(self.saved.iloc[:48], self.at)
        self.assertEqual(len(errors.layout.shapes), 2)
        for shape in errors.layout.shapes:
            self.assertEqual(pd.Timestamp(shape.x0), self.at-pd.Timedelta(minutes=30))
            self.assertEqual(pd.Timestamp(shape.x1), self.at+pd.Timedelta(minutes=30))
        self.assertIn('3px solid', c.table_html(self.raw.head(2), ['date_time']))

    def test_locked_data_artifact_and_core_code_unchanged(self):
        baseline = json.loads((d.ROOT/'docs/uci_first_baseline.json').read_text())
        for name in ['test_predictions.csv', 'test_metrics.csv', 'final_model.joblib']:
            self.assertEqual(d.sha256(d.FINAL/name), baseline[name]['sha256'])
        for name, expected in baseline['protected_code'].items():
            self.assertEqual(d.sha256(Path(name)), expected)


class UciPresentationFlowTests(unittest.TestCase):
    def test_calculation_replay_controls_and_timestamp_reset(self):
        app = self.app()
        app.radio(key='prediction_mode').set_value('Chạy và giải thích từng bước').run()
        app.button(key='show_prediction').click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn('calculation_trace',app.session_state)
        for step in range(1,6):
            app.button(key='calc_next').click().run()
            self.assertEqual(app.session_state['calculation_step'],step)
            self.assertEqual(len(app.exception),0)
        app.button(key='trace_boosting').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.session_state['boosting_trace']),400)
        app.button(key='calc_reset').click().run()
        self.assertEqual(app.session_state['calculation_step'],0)
        app.selectbox(key='at').select(pd.Timestamp('2018-01-19 16:00')).run()
        self.assertNotIn('calculation_trace',app.session_state)
        self.assertNotIn('boosting_trace',app.session_state)

    def app(self):
        return AppTest.from_file(str(d.ROOT/'app.py'), default_timeout=90).run()

    def test_default_uci_walkthrough_state_and_stored_result(self):
        app = self.app()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.tabs), 6)
        self.assertEqual(app.selectbox(key='source').value, 'UCI gốc · toàn bộ dữ liệu')
        self.assertEqual(app.selectbox(key='at').value, pd.Timestamp('2018-01-19 15:00'))
        for step in range(1, 6):
            app.button(key='walk_next').click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.session_state['walk_step'], step)
        app.button(key='walk_back').click().run()
        self.assertEqual(app.session_state['walk_step'], 4)
        app.button(key='walk_reset').click().run()
        self.assertEqual(app.session_state['walk_step'], 0)
        app.radio(key='history_feature').set_value('mean_24h').run()
        self.assertEqual(app.session_state['walk_step'], 0)
        with patch.object(d, 'components', side_effect=AssertionError('stored must not infer')):
            app.button(key='show_prediction').click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state['presentation_prediction'][0]['prediction'], d.saved_test_predictions().prediction.iloc[0])
        app.selectbox(key='at').select(pd.Timestamp('2018-01-19 16:00')).run()
        self.assertNotIn('presentation_prediction', app.session_state)

    def test_error_selection_external_counts_and_lock(self):
        app = self.app()
        at = app.selectbox(key='largest_at').value
        app.button(key='inspect_largest').click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox(key='error_at').value, at)
        app.button(key='open_external').click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.button(key='external_predict').disabled)
        app.selectbox(key='external_policy').select('America/Chicago · có DST').run()
        self.assertEqual(len(app.exception), 0)
        counts = [x.value for x in app.dataframe if 'Thiếu/không ghép' in x.value.columns][0]
        self.assertEqual(counts.loc[counts['Bước'].eq('Ghép theo giả định'), 'Thiếu/không ghép'].iloc[0], 1)
        app.button(key='compare_weather').click().run()
        self.assertEqual(len(app.exception), 0)

    def test_missing_artifact_raw_and_external_do_not_crash(self):
        with patch.object(d, 'ARTIFACT', Path('app/nonexistent_model.joblib')):
            app = self.app()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.radio(key='prediction_mode').options), 1)
            app.button(key='show_prediction').click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertIn('presentation_prediction', app.session_state)
        with patch.object(d, 'UCI_RAW', Path('app/nonexistent_raw.csv')):
            app = self.app()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.tabs), 6)
        with patch.object(d, 'TRAFFIC', Path('app/nonexistent_traffic.csv')):
            app = self.app()
            app.button(key='open_external').click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any('Không mở được nguồn ngoài' in x.value for x in app.error))


if __name__ == '__main__':
    unittest.main()
