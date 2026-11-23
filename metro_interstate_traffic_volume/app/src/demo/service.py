"""Data contract, audit and inference using the project's frozen C30 pipeline.

This module has no Streamlit dependency so it can be integrated into another UI.
External data remains blocked until its owning source contract is verified.
"""

from pathlib import Path
import hashlib
import inspect
import json
import platform

import numpy as np
import pandas as pd

from predict import load_model, prepare_features, predict_hours, read_hourly
from src.features import CONFIG_C, HISTORY_FEATURES, add_history_features
from src.preprocessing import fill_weather
from . import weather as openweather

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT.parent
FINAL = PROJECT / 'notebooks/validation/outputs/final_C30'
ARTIFACT = FINAL / 'final_model.joblib'
UCI = PROJECT / 'data/preprocessed/hourly_unfilled.csv'
UCI_RAW = PROJECT / 'data/Metro_Interstate_Traffic_Volume.csv'
MNDOT = PROJECT / 'data/external/mndot'
TRAFFIC = MNDOT / 'prepared/atr301_westbound_post_uci_2018.csv'
WEATHER = openweather.PREPARED
MANIFEST = MNDOT / 'prepared/atr_2018_manifest.json'
FIELDS = ['date_time', 'temp', 'rain_1h', 'snow_1h', 'clouds_all',
          'weather_main', 'is_holiday', 'traffic_volume']
VERIFIED = 'Đã có · đã xác minh'
UNVERIFIED = 'Đã có · chưa xác minh tương thích'
ABSENT = 'Chưa có dữ liệu'
BLOCKERS = {
    'time': 'Chưa xác minh CST cố định hay America/Chicago, DST và mốc khoảng đo weather.',
    'holiday': 'Chưa có lịch lễ/sự kiện ngoài CSV UCI và chính sách khác biệt được duyệt.',
    'location': 'OpenWeather ở điểm khu vực 44.951424/−93.147145; chưa xác minh điểm weather gốc UCI.',
}


def sha256(path):
    """Hash file contents in chunks, including large fitted artifacts."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def json_file(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def file_token(paths):
    """Content-based cache identity; missing files also invalidate on appearance."""
    return tuple((str(p), sha256(p) if Path(p).is_file() else 'missing') for p in paths)


def audited_bundle():
    """Load only the explicit final artifact and verify its saved manifest/spec."""
    report = json_file(FINAL / 'test_evaluation.json')
    digest = sha256(ARTIFACT)
    if digest != report['output_sha256']['final_model.joblib']:
        raise ValueError('Hash artifact khác biên bản cuối; khóa inference.')
    bundle = load_model(ARTIFACT)
    selected = json_file(FINAL / 'selected_model.json')
    plan = json_file(FINAL / 'final_fit_plan.json')
    plan_hash = hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if bundle['fit_plan_hash'] != plan_hash or report['plan_hash'] != plan_hash:
        raise ValueError('Hash kế hoạch fit không khớp.')
    if len(bundle['models']) != 3 or bundle['spec'] != plan['model']:
        raise ValueError('Artifact phải có ba mô hình và đúng đặc tả fit đã khóa.')
    if bundle['features'] != list(CONFIG_C) or bundle['features'] != selected['features']:
        raise ValueError('Tên/thứ tự C30 không khớp.')
    if bundle['spec']['weights'] != selected['weights']:
        raise ValueError('Trọng số không khớp đặc tả đã khóa.')
    if any(model.n_features_in_ != 30 for model in bundle['models'].values()):
        raise ValueError('Mô hình thành phần không có 30 đầu vào.')
    statistics = bundle['fill_statistics']
    if (not {'temp_by_month_hour', 'temp_fallback', 'rain_median'} <= statistics.keys()
            or not np.isfinite([statistics['temp_fallback'], statistics['rain_median']]).all()
            or not np.isfinite(statistics['temp_by_month_hour'].to_numpy()).all()):
        raise ValueError('Thống kê điền weather thiếu hoặc không hợp lệ.')
    return bundle


def load_uci_sources():
    """Expose the untouched raw CSV and the canonical unique-hour context.

    Keep literal holiday ``None``. Duplicate raw timestamps are displayed, never
    passed directly into history/inference. Split tags follow the locked 70/15/15.
    """
    raw = pd.read_csv(UCI_RAW, keep_default_na=False)
    hourly = read_hourly(UCI)
    hourly['source'] = 'UCI gốc · bảng theo giờ'
    hourly['weather_source'] = 'UCI gốc'
    positions = np.arange(len(hourly))
    hourly['data_split'] = np.where(positions < len(hourly) * 70 // 100, 'Train',
                                  np.where(positions < len(hourly) * 85 // 100, 'Validation', 'Test'))
    return raw, hourly


def load_sources():
    """Keep traffic wall time and weather UTC separate; do not guess a join."""
    uci = read_hourly(UCI)
    traffic = pd.read_csv(TRAFFIC, parse_dates=['date_time'])
    if not traffic.date_time.is_unique or not traffic.date_time.gt(uci.date_time.max()).all():
        raise ValueError('MnDOT cần timestamp duy nhất, chỉ phần sau mốc cuối UCI.')
    context = pd.concat([uci[FIELDS], traffic], ignore_index=True).sort_values('date_time')
    context['source'] = np.where(context.date_time.le(uci.date_time.max()), 'UCI context', 'MnDOT')
    # Unknown external values intentionally remain NaN, not defaults or medians.
    weather = openweather.load()
    return context, traffic, weather, uci.date_time.max()


def synthetic_hourly():
    """Deterministic artificial fixture, never an external evaluation dataset."""
    times = pd.date_range('2019-01-01', periods=241, freq='h')
    return pd.DataFrame({'date_time': times, 'temp': 280.0, 'rain_1h': 0.0,
                         'snow_1h': 0.0, 'clouds_all': 40.0, 'weather_main': 'clouds',
                         'is_holiday': 0, 'traffic_volume': 2500 + 1500 * np.sin(np.arange(241) * np.pi / 12),
                         'source': 'Tổng hợp · không phải quan trắc'})


def quality_grid(hourly, start, end, bundle=None, compatible=False):
    """Hourly denominator and independent overlapping missingness flags.

    History is always computed on the full original context, before selecting
    the requested interval. Missing grid rows are for display, never imputed.
    """
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if end < start:
        raise ValueError('Khoảng kết thúc phải sau hoặc bằng bắt đầu.')
    if not hourly.date_time.is_unique:
        raise ValueError('Timestamp lặp; cần chính sách DST trước khi xử lý.')
    indexed = add_history_features(hourly).set_index('date_time')
    grid = indexed.reindex(pd.date_range(start, end, freq='h', name='date_time'))
    grid['has_record'] = grid.index.isin(indexed.index)
    grid['has_target'] = np.isfinite(pd.to_numeric(grid.traffic_volume, errors='coerce')) & grid.traffic_volume.ge(0)
    grid['has_history'] = np.isfinite(grid[HISTORY_FEATURES]).all(axis=1)
    grid['missing_weather_raw'] = grid[['temp', 'rain_1h', 'snow_1h', 'clouds_all', 'weather_main']].isna().any(axis=1)
    grid['compatible_weather'] = compatible
    grid['input_ready'] = False
    if compatible and bundle is not None:
        times = grid.index[grid.has_record & (grid.index > pd.Timestamp(bundle['train_end']))]
        if len(times):
            features = prepare_features(hourly, times, bundle)
            grid.loc[times, 'input_ready'] = np.isfinite(features).all(axis=1).to_numpy()
    grid['score_ready'] = grid.input_ready & grid.has_target
    counts = {'Giờ kỳ vọng': len(grid), 'Có bản ghi': int(grid.has_record.sum()),
              'Vắng bản ghi': int((~grid.has_record).sum()), 'Có target hợp lệ': int(grid.has_target.sum()),
              'Đủ history': int(grid.has_history.sum()), 'Đủ đầu vào sau xử lý': int(grid.input_ready.sum()),
              'Đủ điều kiện chấm': int(grid.score_ready.sum())}
    return grid, counts


def quality_view(grid, mode='synthetic'):
    """Explain readiness in plain language without changing eligibility rules."""
    rows = []
    for at, row in grid.iterrows():
        reasons = []
        if not row.has_record:
            state, reasons = 'Không có dữ liệu giờ này', ['Nguồn không ghi nhận giờ này; không tự điền số xe bằng 0.']
        else:
            if pd.isna(row.lag_24h):
                reasons.append('Thiếu số xe đúng 24 giờ trước')
            if pd.isna(row.lag_168h):
                reasons.append('Thiếu số xe đúng 7 ngày trước')
            if pd.isna(row.mean_24h):
                reasons.append('Chưa đủ quan sát để tính trung bình 24 giờ trước (cần ít nhất 18 giờ)')
            if mode == 'uci':
                state = 'Xem dữ liệu UCI'
                reasons.append('Giữ nguyên dữ liệu; dự đoán test được đọc từ kết quả đã lưu')
            elif not row.has_history:
                state = 'Thiếu lịch sử'
            elif not row.compatible_weather:
                state = 'Chờ xác minh nguồn'
                reasons.append('Weather đã ghép xem trước; cần chốt thời gian và ngày lễ trước khi dự đoán')
            elif row.input_ready:
                state = 'Có thể dự đoán'
                reasons.append('Đủ đầu vào sau xử lý')
            else:
                state = 'Còn thiếu đầu vào'
                reasons.append('Chưa đủ biến hợp lệ để đưa vào mô hình')
            if not row.has_target:
                reasons.append('Chưa có số xe thực tế để tính sai số')
        rows.append({'Giờ': at, 'Số xe trong giờ': row.traffic_volume,
                     'Trạng thái': state, 'Giải thích': '; '.join(reasons)})
    return pd.DataFrame(rows)


def history_window(hourly, at):
    """Expose exactly the [t-24h,t) observations used for the rolling mean."""
    at = pd.Timestamp(at)
    return hourly.loc[hourly.date_time.ge(at - pd.Timedelta(hours=24)) & hourly.date_time.lt(at),
                      ['date_time', 'traffic_volume', 'source']].copy()


def weather_values(hourly, at, bundle, compatible):
    """Show observed / frozen-rule filled / unresolved status for each input."""
    columns = ['temp', 'rain_1h', 'snow_1h', 'clouds_all', 'weather_main', 'is_holiday']
    at = pd.Timestamp(at)
    before = hourly.loc[hourly.date_time.le(at)].copy()
    original = before.set_index('date_time').loc[at, columns]
    filled = fill_weather(before, bundle['fill_statistics']).set_index('date_time').loc[at, columns] if compatible else original
    table = pd.DataFrame([{'Biến': col, 'Giá trị gốc': str(original[col]), 'Sau xử lý': str(filled[col]),
                          'Trạng thái': ('Chưa xác minh / còn thiếu' if not compatible or pd.isna(filled[col])
                                         else 'Điền theo quy tắc đã khóa' if pd.isna(original[col]) else 'Quan sát trực tiếp')}
                         for col in columns])
    selected = before.set_index('date_time').loc[at]
    if str(selected.get('weather_source', '')).startswith('OpenWeather'):
        for col in openweather.VALUES:
            status = selected.get(col + '_status', 'api_1h')
            description = ('0 theo quy ước vắng hiện tượng · OpenWeather' if status == 'zero_by_provider_omission_rule'
                           else 'Giá trị OpenWeather · ghép giờ theo giả định')
            table.loc[table['Biến'].eq(col), 'Trạng thái'] = description if pd.notna(original[col]) else 'Chưa ghép được giờ weather'
            if status == 'zero_by_provider_omission_rule':
                table.loc[table['Biến'].eq(col), 'Giá trị gốc'] = 'API không trả trường hiện tượng'
    return table


def infer(hourly, times, bundle, compatible=False):
    """Guard external inference and delegate the entire feature/ensemble logic."""
    if not compatible:
        raise ValueError('Dự đoán bị khóa: hợp đồng dữ liệu nguồn chưa được xác minh.')
    return predict_hours(hourly, times, bundle)


def components(hourly, at, bundle, compatible=False):
    """Match predict_hours clipping; weighted components are not feature effects."""
    result = infer(hourly, [at], bundle, compatible)
    if result.prediction.isna().any():
        return result, pd.DataFrame()
    features = prepare_features(hourly, [at], bundle)
    matrix = np.ascontiguousarray(features, dtype='float32')
    rows = []
    for name, model in bundle['models'].items():
        value = float(np.clip(model.predict(matrix), 0, None).astype('float64')[0])
        weight = bundle['spec']['weights'][name]
        rows.append({'Mô hình': name, 'Dự đoán thành phần': value, 'Trọng số': weight,
                     'Giá trị sau nhân trọng số': value * weight})
    parts = pd.DataFrame(rows)
    np.testing.assert_allclose(parts['Giá trị sau nhân trọng số'].sum(), result.prediction.iloc[0], rtol=1e-12)
    return result, parts


def evaluate_range(hourly, start, end, bundle, uci_end, compatible=False):
    """Score the post-UCI intersection only; retain a complete plotting grid."""
    if not compatible:
        raise ValueError('Đánh giá ngoài bị khóa: dữ liệu chưa tương thích.')
    if pd.Timestamp(start) <= pd.Timestamp(uci_end):
        raise ValueError('Khoảng đánh giá phải hoàn toàn sau mốc cuối UCI.')
    grid, counts = quality_grid(hourly, start, end, bundle, compatible)
    times = grid.index[grid.has_record]
    grid['prediction'] = np.nan
    if len(times):
        predicted = infer(hourly, times, bundle, compatible).set_index('date_time')
        grid.loc[times, 'prediction'] = predicted.prediction
    scored = np.isfinite(grid.prediction) & grid.has_target
    grid['absolute_error'] = (grid.prediction - grid.traffic_volume).abs().where(scored)
    counts.update({'Có dự đoán': int(np.isfinite(grid.prediction).sum()), 'Được chấm': int(scored.sum()),
                   'Bị loại (hợp duy nhất)': int((~scored).sum()),
                   'Thiếu history (có bản ghi)': int((grid.has_record & ~grid.has_history).sum()),
                   'Thiếu target (có bản ghi)': int((grid.has_record & ~grid.has_target).sum()),
                   'Đầu vào khác chưa hợp lệ': int((grid.has_record & grid.has_history & ~grid.input_ready).sum())})
    actual, prediction = grid.loc[scored, 'traffic_volume'], grid.loc[scored, 'prediction']
    error = prediction - actual
    metrics = {'n': len(actual), 'MAE': float(error.abs().mean()), 'RMSE': float(np.sqrt((error ** 2).mean())),
               'R2': float(1 - (error ** 2).sum() / ((actual - actual.mean()) ** 2).sum())
               if len(actual) > 1 and actual.var() > 0 else None}
    return grid, counts, metrics


def audit(bundle=None, error=None):
    """Return the requested five-column checklist with explicit evidence."""
    import sklearn
    import xgboost

    plan = json_file(FINAL / 'final_fit_plan.json')
    rows = []
    def row(item, state, evidence, impact, action):
        rows.append(dict(zip(['Hạng mục', 'Trạng thái', 'Bằng chứng/đường dẫn', 'Ảnh hưởng', 'Việc cần làm'],
                             [item, state, evidence, impact, action])))
    row('Artifact cuối / ba mô hình / C30 / trọng số / hash', VERIFIED if bundle else UNVERIFIED if ARTIFACT.exists() else ABSENT,
        str(ARTIFACT.relative_to(PROJECT)), 'Inference' if bundle else str(error), 'Đạt' if bundle else 'Sửa lỗi nạp; không fit lại')
    row('Thống kê điền thiếu', VERIFIED if bundle else UNVERIFIED, 'artifact.fill_statistics',
        'Chỉ temp và rain theo quy tắc khóa; không điền history', 'Không fit median trên MnDOT')
    uci = read_hourly(UCI)
    fit_context = add_history_features(uci).iloc[:len(uci) * 85 // 100]
    fit_context = fit_context.loc[fit_context[HISTORY_FEATURES].notna().all(axis=1)]
    fit_ok = bundle is not None and len(fit_context) == bundle['n_fit'] and str(fit_context.date_time.max()) == bundle['train_end']
    row('Phạm vi fit', VERIFIED if fit_ok else UNVERIFIED, 'final_fit_plan.json; artifact.train_end; hourly_unfilled.csv',
        f"n_fit={len(fit_context)}, đầu={fit_context.date_time.min()}, cuối={fit_context.date_time.max()}",
        'Không dùng mtime làm ngày huấn luyện')
    current = {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__,
               'sklearn': sklearn.__version__, 'xgboost': xgboost.__version__}
    row('Phiên bản thư viện', VERIFIED if current == plan['versions'] else UNVERIFIED,
        'final_fit_plan.json: versions', json.dumps({'fit': plan['versions'], 'runtime': current}),
        'Đối chiếu môi trường khi triển khai')
    code_ok = all(sha256(PROJECT / name) == expected for name, expected in plan['code_sha256'].items())
    row('Code tiền xử lý/inference', VERIFIED if code_ok else UNVERIFIED, 'final_fit_plan.json: code_sha256',
        'So khớp code lúc fit', 'Giữ pipeline dùng chung; kiểm tra khác biệt nếu hash đổi')
    for fn in [load_model, prepare_features, predict_hours]:
        row(fn.__name__, VERIFIED, 'predict.py: ' + str(inspect.signature(fn)),
            'bundle' if fn is load_model else 'DataFrame C30 float32' if fn is prepare_features else 'date_time, prediction, status',
            'Luôn truyền artifact cuối tường minh' if fn is load_model else 'Giữ toàn bộ context trước khi chọn giờ')
    manifest = json_file(MANIFEST)
    raw = pd.read_csv(MNDOT / 'raw/atr_2018.csv')
    selected_raw = raw.loc[raw.station_id.eq(301) & raw.dir_of_travel.eq(7) & raw.lane_of_travel.eq(0)]
    melted = selected_raw.melt(id_vars=['date'], value_vars=[str(h) for h in range(1, 25)],
                                var_name='hour', value_name='raw_volume')
    melted['date_time'] = pd.to_datetime(melted.date) + pd.to_timedelta(melted.hour.astype(int) - 1, unit='h')
    prepared = pd.read_csv(MNDOT / 'prepared/atr301_westbound_2018_hourly.csv', parse_dates=['date_time'])
    reconciled = prepared.merge(melted[['date_time', 'raw_volume']], on='date_time', how='outer', validate='one_to_one')
    overlap = prepared.merge(uci[['date_time', 'traffic_volume']], on='date_time', suffixes=('_mndot', '_uci'), validate='one_to_one')
    exact = overlap.traffic_volume_mndot.eq(overlap.traffic_volume_uci)
    traffic_ok = reconciled.traffic_volume.eq(reconciled.raw_volume).all() and exact.all() and len(overlap) == manifest['overlap_uci']['n']
    row('MnDOT trạm / hướng / tổng làn / giờ 1–24', VERIFIED if traffic_ok else UNVERIFIED, str(MANIFEST.relative_to(PROJECT)),
        json.dumps(manifest['selection']) + f'; giờ h → h−1; kiểm lại raw: {len(reconciled)} giờ; giao UCI: {int(exact.sum())}/{len(overlap)} khớp',
        'Kiểm DST và cờ chất lượng ngoài phần giao')
    ow = openweather.load()
    row('Weather OpenWeather / schema / provenance', VERIFIED,
        str(WEATHER.relative_to(PROJECT)), f'{len(ow)} giờ UTC; K, mm/h, %; nhãn C30; cờ zero theo quy ước nguồn',
        'Đã tích hợp xem trước và đối chiếu UCI; chưa chứng nhận cùng nguồn/thời gian')
    for key, message in BLOCKERS.items():
        exists = WEATHER.exists() if key == 'location' else TRAFFIC.exists() if key == 'time' else False
        row(key, UNVERIFIED if exists else ABSENT, 'data/external/mndot/weather/README.md; atr_2018_manifest.json', message,
            'Khóa dự đoán MnDOT; xem phương án trong demo_data_contract.md')
    row('Bảng giờ chuẩn hóa MnDOT', ABSENT, 'data/external/mndot/processed/hourly_demo.csv',
        'Không xuất CSV giả đủ C30 khi weather/time/holiday chưa chốt', 'Không yêu cầu CSV C30 có sẵn')
    row('Kết quả test UCI đã lưu', VERIFIED if sha256(FINAL / 'test_metrics.csv') == json_file(FINAL / 'test_evaluation.json')['output_sha256']['test_metrics.csv'] else UNVERIFIED,
        'notebooks/validation/outputs/final_C30/test_metrics.csv', 'Chỉ đọc; không gọi lại quy trình test', 'Giữ riêng với điểm MnDOT')
    row('README trạng thái cũ', VERIFIED, 'README.md; data/external/mndot/README.md; app/demo_time_weather.py',
        'Demo B cũ là lịch sử; checkpoint C30 cuối đã tồn tại', 'Xem app/README.md và báo cáo audit hiện tại')
    return pd.DataFrame(rows)


def source_comparison():
    """Describe source overlap and temporal/source shift without model scoring.

    The old cohort is UCI calendar 2018 only, the new cohort is MnDOT strictly
    after the last UCI timestamp. Distributions share bins and use percentages
    so unequal cohort sizes do not create misleading count comparisons.
    """
    uci = read_hourly(UCI)
    old = uci.loc[uci.date_time.dt.year.eq(2018), ['date_time', 'traffic_volume']].copy()
    all_traffic = pd.read_csv(MNDOT / 'prepared/atr301_westbound_2018_hourly.csv', parse_dates=['date_time'])
    new = pd.read_csv(TRAFFIC, parse_dates=['date_time'])
    if not new.date_time.gt(uci.date_time.max()).all():
        raise ValueError('Cohort mới phải sau toàn bộ UCI.')
    overlap = old.merge(all_traffic, on='date_time', how='inner', suffixes=('_uci', '_mndot'), validate='one_to_one')
    overlap['difference'] = overlap.traffic_volume_mndot - overlap.traffic_volume_uci
    summary, cohorts = [], []
    for name, frame in [('UCI cũ · 2018', old), ('MnDOT mới · sau UCI', new)]:
        valid = frame.loc[np.isfinite(frame.traffic_volume) & frame.traffic_volume.ge(0)].copy()
        values = valid.traffic_volume
        expected = len(pd.date_range(frame.date_time.min(), frame.date_time.max(), freq='h'))
        summary.append({'Nguồn': name, 'Từ': str(frame.date_time.min()), 'Đến': str(frame.date_time.max()),
                        'Giờ lịch': expected, 'Có bản ghi': len(frame), 'Target hợp lệ': len(valid),
                        'Vắng bản ghi': expected - len(frame), 'Trung bình': values.mean(), 'Trung vị': values.median(),
                        'Độ lệch chuẩn': values.std(), 'P05': values.quantile(.05), 'P95': values.quantile(.95)})
        cohorts.append(valid.assign(source=name, hour=valid.date_time.dt.hour, weekday=valid.date_time.dt.dayofweek))
    joined = pd.concat(cohorts, ignore_index=True)
    edges = np.linspace(0, max(float(joined.traffic_volume.max()), 1), 31)
    histograms = []
    for name, frame in joined.groupby('source', sort=False):
        frequency, _ = np.histogram(frame.traffic_volume, bins=edges)
        histograms.extend({'Nguồn': name, 'Từ xe/giờ': float(left), 'Đến xe/giờ': float(right),
                           'Tỷ lệ (%)': count / len(frame) * 100, 'Số mẫu': int(count)}
                          for left, right, count in zip(edges[:-1], edges[1:], frequency))
    profile = joined.groupby(['source', 'weekday', 'hour']).traffic_volume.agg(['mean', 'count']).reset_index()
    traffic_grid = pd.concat([old.set_index('date_time').traffic_volume.rename('UCI'),
                              all_traffic.set_index('date_time').traffic_volume.rename('MnDOT')], axis=1, sort=True)
    calendar = pd.date_range(traffic_grid.index.min(), traffic_grid.index.max(), freq='h', name='date_time')
    coverage = pd.DataFrame(index=calendar)
    coverage['has_uci'] = calendar.isin(old.date_time)
    coverage['has_mndot'] = calendar.isin(all_traffic.date_time)
    coverage['Nhóm'] = np.select(
        [coverage.has_uci & coverage.has_mndot,
         ~coverage.has_uci & coverage.has_mndot & (calendar <= uci.date_time.max()),
         ~coverage.has_uci & coverage.has_mndot & (calendar > uci.date_time.max()),
         coverage.has_uci & ~coverage.has_mndot],
        ['Giao timestamp UCI–MnDOT', 'Chỉ MnDOT · trong giai đoạn UCI',
         'Chỉ MnDOT · sau mốc cuối UCI', 'Chỉ UCI'], default='Vắng cả hai nguồn')
    membership = coverage.loc[coverage.has_mndot].groupby('Nhóm', sort=False).size().rename('Số giờ').reset_index()
    membership['Tỷ lệ trên toàn bộ MnDOT (%)'] = membership['Số giờ'] / len(all_traffic) * 100
    daily_coverage = coverage.reset_index().assign(Ngày=lambda frame: frame.date_time.dt.normalize()).groupby(
        ['Ngày', 'Nhóm']).size().rename('Số giờ').reset_index()
    return {'overlap': overlap, 'summary': pd.DataFrame(summary), 'histogram': pd.DataFrame(histograms),
            'profile': profile, 'traffic_grid': traffic_grid, 'membership': membership,
            'daily_coverage': daily_coverage, 'uci_end': uci.date_time.max(), 'n_mndot': len(all_traffic)}


def saved_test_predictions():
    """Read already-saved UCI test predictions only after verifying their hash."""
    path = FINAL / 'test_predictions.csv'
    expected = json_file(FINAL / 'test_evaluation.json')['output_sha256']['test_predictions.csv']
    if sha256(path) != expected:
        raise ValueError('Hash dự đoán test đã lưu không khớp; không dựng biểu đồ từ file này.')
    return pd.read_csv(path, parse_dates=['date_time'])
