"""Dự đoán C30 từ mô hình đã lưu và dữ liệu theo giờ đã chuẩn hóa."""

from pathlib import Path
import argparse

import joblib
import numpy as np
import pandas as pd

from src.features import CONFIG_C, add_time_features, add_weather_features, add_history_features
from src.preprocessing import fill_weather


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = ROOT / 'notebooks/validation/outputs/interpretation_C30/train_C30_interpretation.joblib'


def load_model(path=DEFAULT_MODEL):
    """Nạp artifact; artifact mặc định chỉ fit train, phục vụ validation."""
    if not Path(path).is_file():
        raise FileNotFoundError('Chưa có artifact. Chạy interpretation_C30.ipynb hoặc truyền đường dẫn mô hình đã fit.')
    bundle = joblib.load(path)
    if bundle['features'] != list(CONFIG_C):
        raise ValueError('Thứ tự đặc trưng trong artifact không khớp C30.')
    if set(bundle['models']) != set(bundle['spec']['weights']):
        raise ValueError('Danh sách mô hình không khớp các trọng số đã lưu.')
    if not np.isclose(sum(bundle['spec']['weights'].values()), 1):
        raise ValueError('Tổng trọng số ensemble phải bằng 1.')
    return bundle


def read_hourly(path, nrows=None):
    """Đọc CSV theo giờ; giữ nhãn None và các ô thời tiết thiếu."""
    table = pd.read_csv(path, nrows=nrows, keep_default_na=False,
                        na_values={c: [''] for c in ['temp', 'rain_1h', 'traffic_volume']},
                        float_precision='round_trip')
    table['date_time'] = pd.to_datetime(table.date_time, errors='raise')
    return table


def prepare_features(hourly, times, bundle):
    """Tạo C30 bằng thống kê đã lưu, chỉ dùng target quá khứ cho history.

    hourly gồm các giờ quá khứ và giờ cần dự đoán. traffic_volume tại giờ
    hiện tại có thể để NaN; không được điền bằng dự đoán hoặc dữ liệu tương lai.
    Với nhiều giờ có target thật, đây là kịch bản quan sát tuần tự từng giờ.
    """
    required = {'date_time', 'temp', 'rain_1h', 'snow_1h', 'clouds_all',
                'weather_main', 'is_holiday', 'traffic_volume'}
    missing = required - set(hourly.columns)
    if missing:
        raise ValueError(f'Chưa đủ dữ liệu theo giờ cho C30: {sorted(missing)}')
    requested = pd.DatetimeIndex(pd.to_datetime(list(times)), name='date_time')
    if requested.empty or requested.hasnans or not requested.is_unique:
        raise ValueError('Cần ít nhất một timestamp hợp lệ, không lặp.')
    table = hourly.copy()
    table['date_time'] = pd.to_datetime(table.date_time, errors='raise')
    if table.date_time.dt.tz is not None or requested.tz is not None:
        raise ValueError('Cần chuẩn hóa về cùng quy ước giờ naive đã công bố trước khi dự đoán.')
    if table.date_time.isna().any() or not table.date_time.is_unique:
        raise ValueError('Dữ liệu cần timestamp duy nhất và không thiếu.')
    if not table.date_time.eq(table.date_time.dt.floor('h')).all():
        raise ValueError('Timestamp phải đúng đầu giờ.')
    if requested.min() <= pd.Timestamp(bundle['train_end']):
        raise ValueError('Giờ dự đoán phải nằm sau giai đoạn fit của artifact.')
    absent = requested.difference(table.date_time)
    if len(absent):
        raise ValueError(f'Không có đầu vào weather/calendar tại: {absent.tolist()[:3]}')
    table = table.loc[table.date_time.le(requested.max())].sort_values('date_time')
    # Tạo history từ quan sát gốc, trước khi chọn các giờ cần dự đoán.
    history = add_history_features(table).set_index('date_time')
    filled = fill_weather(table, bundle['fill_statistics'])
    features = add_weather_features(add_time_features(filled)).set_index('date_time')
    features[['lag_24h', 'lag_168h', 'mean_24h']] = history[['lag_24h', 'lag_168h', 'mean_24h']]
    return features.loc[requested, bundle['features']].astype('float32')


def predict_hours(hourly, times, bundle):
    """Dự đoán các giờ đủ C30; giờ thiếu history được trả về với lý do."""
    features = prepare_features(hourly, times, bundle)
    matrix = np.ascontiguousarray(features, dtype='float32')
    ready = np.isfinite(matrix).all(axis=1)
    result = pd.DataFrame({'date_time': features.index, 'prediction': np.nan,
                           'status': 'Thiếu history hoặc đầu vào chưa hợp lệ'})
    if ready.any():
        parts = [bundle['spec']['weights'][name]
                 * np.clip(model.predict(matrix[ready]), 0, None).astype('float64')
                 for name, model in bundle['models'].items()]
        result.loc[ready, 'prediction'] = np.clip(np.sum(parts, axis=0), 0, None)
        result.loc[ready, 'status'] = 'Đủ đầu vào'
    return result


def fit_final():
    """Fit cấu hình đã khóa trên train+validation; tái dùng artifact nếu có.

    Kế hoạch được lưu trước khi chấm test. Thay dữ liệu, tham số hoặc code
    sẽ làm kiểm tra giao thức dừng; hàm không tự mở một lượt test mới.
    """
    import hashlib
    import json
    import platform
    import sklearn
    import xgboost
    from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
    from xgboost import XGBRegressor
    from threadpoolctl import threadpool_limits
    from src import feature_experiments as fe
    from src.features import has_history
    from src.preprocessing import fit_weather_fill

    folder = ROOT / 'notebooks/validation/outputs/final_C30'
    spec = json.loads((folder / 'selected_model.json').read_text(encoding='utf-8'))
    data_path = ROOT / 'data/preprocessed/hourly_unfilled.csv'
    data_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
    if data_hash != spec['dataset_sha256_at_experiment']:
        raise ValueError('Dữ liệu khác phiên bản đã khóa; dừng trước khi đánh giá test.')
    hourly = read_hourly(data_path)
    if not hourly.date_time.is_unique or not hourly.date_time.is_monotonic_increasing:
        raise ValueError('Timestamp cần duy nhất và tăng dần.')
    featured = add_history_features(add_weather_features(add_time_features(hourly)))
    cut = len(hourly) * 85 // 100
    fit = featured.iloc[:cut].loc[lambda d: has_history(d)]
    test = featured.iloc[cut:]
    eligible = test.loc[has_history(test)]
    x_fit, _, fill_log = fe.prepare_fold(hourly, featured, fit.date_time, eligible.date_time)
    frozen = {k: spec[k] for k in ['model_id', 'config', 'features', 'weights', 'components', 'preprocessing']}
    plan = {'model': frozen, 'data_sha256': data_hash, 'full_frame_hash': fe.frame_hash(hourly),
            'fit_hash': fe.frame_hash(fit[['date_time', 'traffic_volume']]),
            'test_times_hash': fe.frame_hash(test[['date_time']]), 'n_fit': len(fit),
            'n_test_total': len(test), 'n_test_history': len(eligible), 'preprocessing': fill_log,
            'seed': 42, 'scenario': 'sequential hourly; observed past traffic; same-hour weather assumed available',
            'thread_policy': 'RF/XGB fit under threadpool_limits(1), ExtraTrees unchanged',
            'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__,
                         'sklearn': sklearn.__version__, 'xgboost': xgboost.__version__},
            'code_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ['predict.py', 'src/features.py', 'src/preprocessing.py', 'src/feature_experiments.py']}}
    plan_hash = hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    plan_path, artifact = folder / 'final_fit_plan.json', folder / 'final_model.joblib'
    if plan_path.exists():
        if json.loads(plan_path.read_text(encoding='utf-8')) != plan:
            raise ValueError('Giao thức đã đổi; không tự fit hoặc chấm test lại.')
    else:
        with plan_path.open('x', encoding='utf-8') as file:
            json.dump(plan, file, ensure_ascii=False, indent=2)
    if artifact.exists():
        bundle = load_model(artifact)
        if bundle['fit_plan_hash'] != plan_hash:
            raise ValueError('Artifact không thuộc kế hoạch đã khóa.')
        print('Nạp lại mô hình fit cuối đã lưu.')
    else:
        if (folder / 'test_evaluation.started.json').exists() or (folder / 'test_evaluation.json').exists():
            raise ValueError('Đã bắt đầu test; không tự fit lại mô hình.')
        models, matrix = {}, np.ascontiguousarray(x_fit[spec['features']], dtype='float32')
        for name, constructor in {'Random Forest': RandomForestRegressor, 'XGBoost': XGBRegressor,
                                  'ExtraTrees': ExtraTreesRegressor}.items():
            params = spec['components'][name]['params'].copy()
            if name == 'XGBoost':
                params.pop('missing', None)
            with threadpool_limits(limits=1 if name != 'ExtraTrees' else None):
                models[name] = constructor(**params).fit(matrix, fit.traffic_volume.to_numpy())
            print(f'Đã fit {name}.', flush=True)
        bundle = {'scope': 'final fit on train+validation complete-history cohort', 'models': models,
                  'spec': frozen, 'features': spec['features'], 'fit_plan_hash': plan_hash,
                  'fill_statistics': fit_weather_fill(hourly.set_index('date_time', drop=False).loc[fit.date_time]),
                  'train_end': str(fit.date_time.max()), 'n_fit': len(fit)}
        joblib.dump(bundle, artifact, compress=3)
    return bundle, hourly, plan


def evaluate_test_once(hourly, bundle):
    """Chấm test một lần; lần sau chỉ đọc kết quả và kiểm tra hash.

    Nếu lượt đầu bị ngắt sau dấu bắt đầu, dừng để kiểm tra thay vì tự chấm lại.
    Không thay tham số hoặc trọng số dựa vào điểm test.
    """
    import hashlib
    import json
    from src.feature_experiments import frame_hash
    from src.features import has_history
    from src.evaluation import regression_metrics

    folder = ROOT / 'notebooks/validation/outputs/final_C30'
    report_path = folder / 'test_evaluation.json'
    plan = json.loads((folder / 'final_fit_plan.json').read_text(encoding='utf-8'))
    plan_hash = hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if bundle['fit_plan_hash'] != plan_hash or frame_hash(hourly) != plan['full_frame_hash']:
        raise ValueError('Mô hình hoặc dữ liệu không khớp kế hoạch test.')
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding='utf-8'))
        if report['plan_hash'] != plan_hash:
            raise ValueError('Báo cáo test không khớp kế hoạch.')
        for name, expected in report['output_sha256'].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f'File kết quả đã thay đổi: {name}')
        predictions = pd.read_csv(folder / 'test_predictions.csv', parse_dates=['date_time'])
        metrics = pd.read_csv(folder / 'test_metrics.csv')
        print('Đọc lại kết quả test đã lưu; không dự đoán hoặc chấm lại.')
    else:
        with (folder / 'test_evaluation.started.json').open('x', encoding='utf-8') as file:
            json.dump({'plan_hash': plan_hash, 'rule': 'Inspect interrupted evaluation before retry.'}, file)
        test = hourly.iloc[len(hourly) * 85 // 100:]
        predictions = predict_hours(hourly, test.date_time, bundle)
        np.testing.assert_array_equal(predictions.date_time.to_numpy(), test.date_time.to_numpy())
        predictions['actual'] = test.traffic_volume.to_numpy()
        scored = predictions.prediction.notna()
        expected = add_history_features(hourly).iloc[len(hourly) * 85 // 100:]
        np.testing.assert_array_equal(scored.to_numpy(), has_history(expected).to_numpy())
        predictions['absolute_error'] = (predictions.prediction - predictions.actual).abs()
        values = regression_metrics(predictions.loc[scored, 'actual'], predictions.loc[scored, 'prediction'])
        metrics = pd.DataFrame([{'model': bundle['spec']['model_id'], 'config': 'C30', 'n_fit': bundle['n_fit'],
                                 'n_test_total': len(test), 'n': int(scored.sum()), 'n_excluded': int((~scored).sum()),
                                 'start': str(predictions.loc[scored, 'date_time'].min()),
                                 'end': str(predictions.loc[scored, 'date_time'].max()), **values}])
        predictions.to_csv(folder / 'test_predictions.csv', index=False)
        metrics.to_csv(folder / 'test_metrics.csv', index=False)
        outputs = ['test_predictions.csv', 'test_metrics.csv', 'final_model.joblib']
        report = {'plan_hash': plan_hash, 'status': 'complete', 'test_evaluated': True, 'retuned': False,
                  'metrics': metrics.iloc[0].to_dict(), 'scenario': plan['scenario'],
                  'validation_previously_seen': True,
                  'output_sha256': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in outputs}}
        with report_path.open('x', encoding='utf-8') as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
    # Chỉ cập nhật trạng thái, giữ nguyên cấu hình và số liệu validation cũ.
    spec_path = folder / 'selected_model.json'
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    spec.update({'status': 'final_refit_and_test_completed', 'refit_completed': True, 'test_evaluated': True,
                 'final_fit_n': bundle['n_fit'], 'final_fit_end': bundle['train_end'],
                 'final_artifact': str((folder / 'final_model.joblib').relative_to(ROOT)),
                 'test_report': str(report_path.relative_to(ROOT)), 'test_metrics': report['metrics'],
                 'next_step': 'Use saved final artifact for demo; do not retune using test.'})
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
    return predictions, metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='CSV đã chuẩn hóa, gồm cả ngữ cảnh quá khứ')
    parser.add_argument('--model', type=Path, default=DEFAULT_MODEL)
    parser.add_argument('--at', nargs='+', required=True, help='Các timestamp cần dự đoán')
    parser.add_argument('--output', type=Path, help='CSV kết quả, nếu cần lưu')
    args = parser.parse_args()
    bundle = load_model(args.model)
    output = predict_hours(read_hourly(args.input), args.at, bundle)
    print(f"Phạm vi artifact: {bundle['scope']}")
    print(output.to_string(index=False))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output.to_csv(args.output, index=False)
