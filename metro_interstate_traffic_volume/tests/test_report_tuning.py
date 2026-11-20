"""Cùng protocol/fold/ngân sách; không điền median cho lag."""
import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from sklearn.model_selection import ParameterSampler
import numpy as np
import pandas as pd
from src.model import CONFIGS, SEARCH_SPACE, make_cv_model
from src.tuning_cv import candidate_bank, validate_records, _digest, block_bootstrap_deltas, _write, SEED, N_CANDIDATES


class ReportTuningTests(unittest.TestCase):
    def test_atomic_write_retries_transient_windows_lock(self):
        with TemporaryDirectory() as directory:
            destination=Path(directory)/'results.json'
            replace=Path.replace
            attempts=[]
            def locked_once(path,target):
                attempts.append(1)
                if len(attempts)==1:raise PermissionError('transient reader')
                return replace(path,target)
            with patch.object(Path,'replace',locked_once),patch('src.tuning_cv.time.sleep'):
                _write(destination,{'complete':True})
            self.assertEqual(len(attempts),2)
            self.assertEqual(json.loads(destination.read_text(encoding='utf-8')),{'complete':True})

    def test_equal_budget_and_valid_parameters(self):
        for name,candidates in candidate_bank().items():
            self.assertEqual(len(candidates),6)
            self.assertEqual(len({_digest(p) for p in candidates}),6)
            for parameters in candidates:
                make_cv_model(name,CONFIGS['C30']).set_params(**parameters)

    def test_RF_samples_budget_directly_instead_of_grid_prefix(self):
        actual=candidate_bank()['Random Forest']
        expected=list(ParameterSampler(SEARCH_SPACE['Random Forest'],n_iter=N_CANDIDATES,random_state=SEED))
        self.assertEqual(actual,expected)
        self.assertGreater(len({p['model__max_depth'] for p in actual}),1)
        self.assertGreater(len({p['model__max_features'] for p in actual}),1)
        self.assertIn(2,SEARCH_SPACE['Random Forest']['model__min_samples_leaf'])
        self.assertIn(.33,SEARCH_SPACE['Random Forest']['model__max_features'])

    def test_nan_lag_is_rejected_not_median_filled(self):
        frame=pd.DataFrame({c:[1.,2.] for c in CONFIGS['C30']})
        frame['weekday_hour']=[1,2]
        frame.loc[0,'lag_24h']=np.nan
        with self.assertRaisesRegex(ValueError,'NaN/inf'):
            make_cv_model('Random Forest',CONFIGS['C30']).fit(frame,[10,20])

    def test_ridge_uses_weekday_hour(self):
        frame=pd.DataFrame({c:np.ones(24) for c in CONFIGS['C30']})
        frame['weekday_hour']=np.arange(24)
        model=make_cv_model('Ridge',CONFIGS['C30']).fit(frame,np.arange(24))
        self.assertLess(np.abs(model.predict(frame)-np.arange(24)).mean(),5)
        self.assertIn('calendar__weekday_hour',str(model.named_steps['columns'].get_feature_names_out()))

    def test_protocol_mismatch_stops_before_reading_scores(self):
        with self.assertRaisesRegex(ValueError,'Protocol hash'):
            validate_records({'A12':{'x':1},'B27':{'x':2},'C30':{'x':1}},
                             {'A12':{},'B27':{},'C30':{}})

    def test_calendar_block_bootstrap_preserves_direction_and_gaps(self):
        times=pd.date_range('2020-01-01',periods=24*20,freq='h').delete(np.arange(24*7,24*10))
        observations=[dict(fold=1,date_time=str(t),y_true=100.) for t in times]
        records={}
        for config,error in [('A12',10.),('B27',5.),('C30',1.)]:
            records[config]=dict(oof_observations=observations,
                                 results=[dict(model='synthetic',oof_prediction=[100.+error]*len(times))])
        rows=block_bootstrap_deltas({'records':records},reps=100)
        np.testing.assert_allclose(rows.MAE_gain,[5.,4.])
        np.testing.assert_allclose(rows.CI95_low,[5.,4.])
        np.testing.assert_allclose(rows.CI95_high,[5.,4.])


if __name__=='__main__':unittest.main()
