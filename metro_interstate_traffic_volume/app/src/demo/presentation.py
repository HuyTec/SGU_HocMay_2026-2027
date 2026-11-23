"""Read-only educational views over the frozen C30 pipeline.

No training, new preprocessing fit, or test-evaluation entry point is used here.
Metrics below only summarize already-saved predictions in an explicit scope.
"""

import numpy as np
import pandas as pd

from . import service as demo
from src.preprocessing import build_hourly_target, build_hourly_weather, merge_hourly_data, split_by_time
from src.features import add_time_features, add_weather_features, add_history_features, has_history

STEPS = ['CSV gốc', 'Timestamp trùng', 'Gộp đúng một giờ',
         'Ngoại lệ và giá trị thiếu', 'Mã hóa và đặc trưng', 'Chia theo thời gian']
FEATURE_LABELS = {'lag_24h': 'Số xe 24 giờ trước', 'lag_168h': 'Số xe 7 ngày trước',
                  'mean_24h': 'Trung bình 24 giờ trước'}


def metrics(frame):
    """Summarize supplied saved rows, preserving excluded rows in denominator."""
    valid = frame.loc[np.isfinite(frame.prediction) & np.isfinite(frame.actual) & frame.actual.ge(0)]
    error = valid.prediction - valid.actual
    denominator = ((valid.actual - valid.actual.mean()) ** 2).sum()
    return {'n_total': len(frame), 'n': len(valid), 'n_excluded': len(frame) - len(valid),
            'MAE': float(error.abs().mean()) if len(valid) else None,
            'RMSE': float(np.sqrt((error ** 2).mean())) if len(valid) else None,
            'R2': float(1 - (error ** 2).sum() / denominator) if len(valid) > 1 and denominator > 0 else None}


def verified_results():
    """Verify saved files and reproduce metrics from those files, without models."""
    report = demo.json_file(demo.FINAL / 'test_evaluation.json')
    metric_path = demo.FINAL / 'test_metrics.csv'
    if demo.sha256(metric_path) != report['output_sha256']['test_metrics.csv']:
        raise ValueError('Hash test_metrics.csv không khớp biên bản.')
    saved = demo.saved_test_predictions()
    measured = metrics(saved)
    for name in ['MAE', 'RMSE', 'R2']:
        if not np.isclose(measured[name], report['metrics'][name], rtol=0, atol=1e-9):
            raise ValueError('Metric từ dự đoán lưu không khớp báo cáo: ' + name)
    if measured['n'] != report['metrics']['n'] or measured['n_total'] != report['metrics']['n_test_total']:
        raise ValueError('Số mẫu test không khớp biên bản.')
    return saved, report, measured


def split_summary(hourly):
    """Reuse chronological split and exact history rules, no learned transform."""
    history = add_history_features(hourly)
    rows = []
    for name, frame in split_by_time(history).items():
        rows.append({'Tập': name, 'Số giờ quan sát': len(frame), 'Đủ history': int(has_history(frame).sum()),
                     'Từ': frame.date_time.min(), 'Đến': frame.date_time.max()})
    return pd.DataFrame(rows)


def duplicate_example(raw, hourly):
    """Run owning deterministic functions on every raw row of one duplicate hour."""
    count = raw.groupby('date_time', sort=False).size()
    at = count.loc[count.gt(1)].index[0]
    before = raw.loc[raw.date_time.eq(at)].copy()
    after = merge_hourly_data(build_hourly_target(before), build_hourly_weather(before))
    expected = hourly.loc[hourly.date_time.eq(pd.Timestamp(at))]
    for name in ['traffic_volume', 'temp', 'rain_1h', 'snow_1h', 'clouds_all']:
        np.testing.assert_allclose(after[name], expected[name], equal_nan=True)
    if after.weather_main.iloc[0] != expected.weather_main.iloc[0]:
        raise ValueError('Ví dụ gộp weather khác bảng chuẩn.')
    return before, after


def cleaning_example(raw, hourly, case='temp'):
    """Show actual 0 K / flagged rain masking, not fabricated observations."""
    suspicious = raw.temp.eq(0) if case == 'temp' else raw.rain_1h.eq(9831.3)
    if not suspicious.any():
        raise ValueError('Không tìm thấy ngoại lệ này trong CSV hiện tại.')
    at = raw.loc[suspicious, 'date_time'].iloc[0]
    before = raw.loc[raw.date_time.eq(at)].copy()
    after = build_hourly_weather(before)
    expected = hourly.loc[hourly.date_time.eq(pd.Timestamp(at))]
    col = 'temp' if case == 'temp' else 'rain_1h'
    np.testing.assert_allclose(after[col], expected[col], equal_nan=True)
    return before, after


def history_cells(hourly, at, feature='lag_24h'):
    """169 real-hour cells; flags identify exactly which observations are used."""
    if feature not in FEATURE_LABELS:
        raise ValueError('Chọn lag_24h, lag_168h hoặc mean_24h.')
    at = pd.Timestamp(at)
    if not hourly.date_time.is_unique:
        raise ValueError('Cần bảng theo giờ duy nhất trước khi tạo timeline.')
    times = pd.date_range(at - pd.Timedelta(hours=168), at, freq='h', name='date_time')
    cells = hourly.set_index('date_time')[['traffic_volume']].reindex(times).reset_index()
    if feature == 'mean_24h':
        cells['in_window'] = cells.date_time.ge(at - pd.Timedelta(hours=24)) & cells.date_time.lt(at)
    else:
        offset = 24 if feature == 'lag_24h' else 168
        cells['in_window'] = cells.date_time.eq(at - pd.Timedelta(hours=offset))
    cells['is_used'] = cells.in_window & cells.traffic_volume.notna()
    cells['is_current'] = cells.date_time.eq(at)
    cells['label'] = np.where(cells.is_current, 't: target không tham gia history',
                             np.where(cells.is_used, 'Được dùng trong ' + feature,
                                      np.where(cells.in_window, 'Thiếu quan sát cần dùng', 'Ngoài feature đang xem')))
    cells['offset_hours'] = ((cells.date_time - at).dt.total_seconds() / 3600).astype(int)
    return cells


def inspected_features(hourly, at, bundle):
    """Feature vector comes exclusively from the shared frozen inference code."""
    features = demo.prepare_features(hourly, [at], bundle)
    if list(features) != bundle['features'] or not (features.dtypes == 'float32').all():
        raise ValueError('Schema/kiểu C30 không khớp artifact.')
    return features


def one_hour(hourly, at, saved, bundle=None, mode='stored'):
    """Explicit saved lookup or real one-hour inference; never an invented result."""
    at = pd.Timestamp(at)
    selected = saved.loc[saved.date_time.eq(at)]
    if len(selected) != 1:
        raise ValueError('Giờ này không có trong file dự đoán test đã lưu.')
    original = selected.iloc[0]
    parts = pd.DataFrame()
    if mode == 'stored':
        value = original.prediction
    elif mode == 'live':
        if bundle is None:
            raise ValueError('Chưa có artifact hợp lệ để inference trực tiếp.')
        features = inspected_features(hourly, at, bundle)
        if not np.isfinite(features.to_numpy()).all():
            raise ValueError('Giờ này chưa đủ history hoặc weather để tạo C30.')
        predicted, parts = demo.components(hourly, at, bundle, compatible=True)
        value = predicted.prediction.iloc[0]
        if not np.isclose(value, original.prediction, rtol=0, atol=1e-5):
            raise ValueError('Live inference không khớp dự đoán đã lưu; dừng trình diễn kết quả.')
    else:
        raise ValueError('Chế độ dự đoán không được hỗ trợ.')
    return {'date_time': at, 'prediction': value, 'actual': original.actual,
            'absolute_error': abs(value - original.actual), 'mode': mode,
            'status': original.status}, parts


def error_slices(saved):
    """Group saved test errors by public calendar rules with explicit n."""
    frame = saved.loc[saved.prediction.notna() & saved.actual.notna()].copy()
    frame['Giờ'] = frame.date_time.dt.hour
    frame['Loại ngày'] = np.where(frame.date_time.dt.dayofweek.ge(5), 'Cuối tuần', 'Ngày thường')
    frame['Cao điểm'] = np.where(frame.date_time.dt.dayofweek.lt(5) & frame.date_time.dt.hour.isin([6, 7, 8, 15, 16, 17]),
                                'Cao điểm ngày thường', 'Ngoài cao điểm')
    frame['error'] = frame.prediction - frame.actual
    rows = []
    for dimension in ['Giờ', 'Loại ngày', 'Cao điểm']:
        for group, data in frame.groupby(dimension):
            rows.append({'Chiều phân tích': dimension, 'Nhóm': str(group), 'n': len(data),
                         'MAE': data.error.abs().mean(), 'RMSE': np.sqrt(data.error.pow(2).mean())})
    return pd.DataFrame(rows)
