"""Kiểm tra cô lập holdout, tính nhân quả và hợp đồng tuning báo cáo."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.model import CONFIGS, MODEL_NAMES, HourlyFeatures, make_model
from src.tuning import candidate_parameters, load_training_data, run_tuning, fit_selected_model


def synthetic_hourly(n=500):
    times = pd.date_range('2020-01-01',periods=n,freq='h')
    return pd.DataFrame(dict(date_time=times, traffic_volume=(1000+300*np.sin(np.arange(n)/24)).astype(int),
        temp=280.+np.sin(np.arange(n)/8),rain_1h=0.,snow_1h=0.,clouds_all=30.,
        weather_main='clear',weather_description='sky is clear',holiday_name='None',is_holiday=0))


class ReportTuningTests(unittest.TestCase):
    def test_loader_does_not_load_holdout_targets(self):
        with TemporaryDirectory() as directory:
            frame = synthetic_hourly()
            frame['traffic_volume'] = frame.traffic_volume.astype(object)
            frame.loc[350:, 'traffic_volume'] = 'HOLDOUT_MUST_NOT_BE_READ'
            path = Path(directory)/'hourly.csv'
            frame.to_csv(path,index=False)
            read_csv = pd.read_csv
            with patch('src.tuning.pd.read_csv',wraps=read_csv) as reader:
                data = load_training_data(path)
            self.assertEqual(len(data.frame),350)
            self.assertEqual(reader.call_args_list[0].kwargs['usecols'],['date_time'])
            self.assertEqual(reader.call_args_list[1].kwargs['nrows'],350)

    def test_median_only_fit_rows_and_no_future_temperature(self):
        frame = synthetic_hourly()
        frame.loc[0,'temp'] = np.nan
        transformer = HourlyFeatures(CONFIGS['B27'],frame[['date_time','temp']]).fit(frame.iloc[:100])
        self.assertEqual(transformer.statistics_['temp_fallback'],frame.temp.iloc[:100].median())
        probe = frame.iloc[100:150].copy()
        probe.loc[probe.index[0],'temp'] = np.nan
        before = transformer.transform(probe)
        altered = frame[['date_time','temp']].copy()
        altered.loc[altered.date_time.gt(probe.date_time.iloc[20]),'temp'] = 999.
        transformer.weather_context = altered
        after = transformer.transform(probe)
        np.testing.assert_array_equal(before[:21],after[:21])

    def test_equal_unique_budget_and_fresh_pipeline(self):
        for name in MODEL_NAMES:
            candidates = candidate_parameters(name)
            self.assertEqual(len(candidates),6)
            self.assertEqual(len({json.dumps(p,sort_keys=True) for p in candidates}),6)
            model = make_model(name,CONFIGS['A12'])
            self.assertFalse(hasattr(model.named_steps['features'],'statistics_'))
        with self.assertRaises(ValueError):candidate_parameters('Ridge',7)

    def test_cv_results_one_file_and_same_folds_for_AB(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'hourly.csv';synthetic_hourly().to_csv(path,index=False)
            data=load_training_data(path)
            output=Path(directory)/'tuning_results.json'
            result=run_tuning(data,model_names=('Ridge',),n_candidates=1,n_splits=2,output_path=output)
            saved=json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(len(saved['results']),2)
            self.assertEqual([r['score_sha256'] for r in saved['results'][0]['candidates'][0]['folds']],
                             [r['score_sha256'] for r in saved['results'][1]['candidates'][0]['folds']])
            for item in saved['results']:
                self.assertEqual(len(item['oof_prediction']),len(saved['oof_observations']))
            fitted=fit_selected_model(data,result['results'][0])
            self.assertEqual(fitted.named_steps['features'].n_fit_,len(data.frame))

    def test_C_uses_common_history_cohort(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'hourly.csv';synthetic_hourly().to_csv(path,index=False)
            data=load_training_data(path,configs=('A12','B27','C30'))
            self.assertEqual(len(data.frame),350-168)
            self.assertTrue(data.frame[['lag_24h','lag_168h','mean_24h']].notna().all().all())


if __name__=='__main__':
    unittest.main()
