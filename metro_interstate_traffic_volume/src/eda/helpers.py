"""Đọc dữ liệu, thống kê và vẽ hình dùng chung cho ba notebook EDA."""
import hashlib
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display
from src.data import build_hourly_table, load_raw
from src.features import CONFIG_A, CONFIG_B, CONFIG_C, HISTORY_FEATURES, RUSH_HOURS, WEATHER_GROUPS, add_time_features, add_weather_features
SEED = 42
MIN_GROUP = 30
BOOTSTRAPS = 400
BLOCK_DAYS = 7
MIN_HISTORY = 18
SECTION_TITLES = ['Câu hỏi và giả thuyết', 'Ý tưởng tách đặc trưng', 'Đặc trưng được tạo', 'Chất lượng và phân phối', 'Quan hệ với mục tiêu', 'Rủi ro rò rỉ và độ ổn định', 'Quyết định']
sns.set_theme(style='whitegrid', font='DejaVu Sans', font_scale=1.05)
plt.rcParams.update({'figure.dpi': 110, 'savefig.dpi': 160})

def causal_history(frame, min_observations=18):
    """Thêm lag/mean chỉ dùng y trước t; cửa sổ mean là [t-24h,t).

    min_observations điều khiển số giờ tối thiểu có quan sát trong cửa sổ.
    Cột strict luôn yêu cầu đủ 24 giờ, chỉ phục vụ kiểm tra độ phủ.
    """
    times = frame['date_time']
    if not times.is_unique or not times.is_monotonic_increasing or times.isna().any():
        raise ValueError('Cần timestamp duy nhất, không thiếu và tăng dần.')
    if not times.eq(times.dt.floor('h')).all():
        raise ValueError('Timestamp phải nằm đúng mốc giờ.')
    if not 1 <= min_observations <= 24:
        raise ValueError('min_observations phải nằm trong [1,24].')
    result = frame.copy()
    series = result.set_index('date_time').traffic_volume
    for hours in [24, 168]:
        result[f'lag_{hours}h'] = (times - pd.Timedelta(hours=hours)).map(series)
    rolling = series.rolling('24h', closed='left', min_periods=1)
    result['n_history_24h'] = times.map(rolling.count()).fillna(0).astype(int)
    result['mean_24h'] = times.map(rolling.mean()).mask(result.n_history_24h.lt(min_observations))
    result['mean_24h_strict'] = result.mean_24h.where(result.n_history_24h.eq(24))
    return result

def say(text):
    """Hiển thị lời giải thích động, lấy số liệu trực tiếp từ kết quả."""
    display(Markdown(text))

def table(frame):
    """Mọi bảng hiển thị phải chỉ rõ cột n (số mẫu dùng cho hàng đó)."""
    if 'n' not in frame.columns:
        raise ValueError('Bảng thiếu cột n: cần chỉ rõ số mẫu thực tế.')
    display(frame)

def load_context(root):
    """Kiểm toán toàn CSV, nhưng chỉ trả target train cho phân tích feature."""
    root = Path(root)
    path = root / 'data' / 'Metro_Interstate_Traffic_Volume.csv'
    raw = load_raw(path)
    unique_times = pd.DatetimeIndex(raw.date_time.unique()).sort_values()
    expected = pd.date_range(unique_times.min(), unique_times.max(), freq='h')
    measurements = {'rows': len(raw), 'columns': len(raw.columns), 'unique_timestamps': len(unique_times), 'extra_timestamp_rows': len(raw) - len(unique_times), 'missing_hours': len(expected.difference(unique_times))}
    reference = dict(rows=48204, columns=9, unique_timestamps=40575, extra_timestamp_rows=7629, missing_hours=11976)
    audit = pd.DataFrame([dict(item=k, observed=v, expected=reference[k], matches=v == reference[k], n=len(raw)) for k, v in measurements.items()])
    if not audit.matches.all():
        raise ValueError('Số liệu khác mốc người dùng cung cấp:\n' + audit.to_string(index=False))
    expected_endpoints = (pd.Timestamp('2012-10-02 09:00'), pd.Timestamp('2018-09-30 23:00'))
    if (unique_times.min(), unique_times.max()) != expected_endpoints:
        raise ValueError('Mốc đầu/cuối CSV khác yêu cầu; cần xác minh phiên bản dữ liệu.')
    hourly = build_hourly_table(raw, mask_stuck_temp=False, complete_holidays=False)
    train_stop = len(hourly) * 70 // 100
    validation_stop = len(hourly) * 85 // 100
    splits = [('train', hourly.iloc[:train_stop]), ('validation', hourly.iloc[train_stop:validation_stop]), ('test', hourly.iloc[validation_stop:])]
    split_table = pd.DataFrame([dict(split=name, start=part.date_time.min(), end=part.date_time.max(), n=len(part)) for name, part in splits])
    train = add_weather_features(add_time_features(hourly.iloc[:train_stop].copy()))
    train = causal_history(train, min_observations=MIN_HISTORY)
    figures = root / 'figures'
    outputs = root / 'notebooks' / 'eda' / 'outputs'
    figures.mkdir(exist_ok=True)
    outputs.mkdir(parents=True, exist_ok=True)
    rain_main = raw.weather_main.str.strip().str.casefold().eq('rain')
    rain_description = raw.weather_description.str.contains(r'rain', case=False, regex=True)
    rain_audit = pd.DataFrame([dict(scope='Toàn CSV: kiểm toán nhãn', rule=rule, zero_rain_rows=int((raw.rain_1h.eq(0) & mask).sum()), zero_rain_hours=int(raw.loc[raw.rain_1h.eq(0) & mask, 'date_time'].nunique()), n=len(raw)) for rule, mask in [('weather_main = Rain', rain_main), ('weather_description chứa từ rain', rain_description), ('một trong hai nhãn', rain_main | rain_description)]])
    return dict(root=root, path=path, raw=raw.loc[raw.date_time.le(train.date_time.max())].copy(), rain_audit=rain_audit, train=train, audit=audit, splits=split_table, figures=figures, outputs=outputs, sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def audit_context(ctx):
    """Báo kiểm toán số liệu và metadata bộ chia, không mô tả target test."""
    table(ctx['audit'])
    table(ctx['splits'])
    say(f"Các số kiểm toán khớp mốc cung cấp; phân tích feature bên dưới dùng **{len(ctx['train']):,} giờ train**, chưa chấm validation/test. Timestamp không có timezone; chưa phân tích DST (đổi giờ mùa hè). Nhãn lễ lấy theo ngày có ghi trong CSV, chưa tự bổ sung lịch ngoài. Nhãn hiếm đánh dấu khi n < 30; đây là ngưỡng mô tả, không phải kiểm định.")

def feature_spec(ctx, letter):
    """Lập từ điển feature và n quan sát không thiếu cho từng feature."""
    features = {'A': CONFIG_A, 'B': CONFIG_B, 'C': CONFIG_C}[letter]
    rows = []
    formulas = {'hour': 'date_time.dt.hour', 'day_of_week': 'date_time.dt.dayofweek (Monday=0)', 'month': 'date_time.dt.month', 'is_weekend': 'day_of_week >= 5', 'is_rush_hour': f'hour thuộc {RUSH_HOURS} và is_weekend=0', 'is_holiday': 'ngày có holiday khác "None" trong CSV', 'temp_c': 'temp - 273.15', 'rain_1h': 'median giá trị phân biệt mỗi giờ (mm)', 'snow_1h': 'median giá trị phân biệt mỗi giờ (mm)', 'clouds_all': 'median giá trị phân biệt mỗi giờ (%)', 'lag_24h': 'traffic_volume(t-24h), tra timestamp', 'lag_168h': 'traffic_volume(t-168h), tra timestamp', 'mean_24h': 'mean y trong [t-24h,t), ít nhất 18/24 quan sát'}
    for col in features:
        if col.startswith('weather_'):
            formula = f"1 nếu nhãn {col.removeprefix('weather_')} có trong giờ"
            source = 'weather_main'
            missing = 'danh sách nhãn cố định; kiểm tra nhãn lạ theo fold'
        elif col.endswith(('_sin', '_cos')):
            origin, func = col.rsplit('_', 1)
            period = {'hour': 24, 'day_of_week': 7, 'month': 12}[origin]
            formula = f"{func}(2*pi*({origin}{('-1' if origin == 'month' else '')})/{period})"
            source = 'date_time'
            missing = 'không thiếu sau kiểm tra timestamp'
        else:
            formula = formulas[col]
            source = 'traffic_volume, date_time' if col in HISTORY_FEATURES else 'holiday, date_time' if col == 'is_holiday' else 'temp' if col == 'temp_c' else col if col in ['rain_1h', 'snow_1h', 'clouds_all'] else 'date_time'
            missing = 'giữ NaN; cohort đủ history; không điền target' if col in HISTORY_FEATURES else 'mask 0 K/điểm mưa nghi vấn; median chỉ fit fold-train' if col in ['temp_c', 'rain_1h'] else 'không thiếu sau kiểm tra; chưa biết lễ bị bỏ sót'
        rows.append(dict(feature=col, formula=formula, dtype=str(ctx['train'][col].dtype), source=source, missing_rule=missing, n=int(ctx['train'][col].notna().sum())))
    return pd.DataFrame(rows)

def quality(frame, features):
    """Thống kê thiếu và miền giá trị mà không điền thiếu."""
    return pd.DataFrame([dict(feature=f, missing=int(frame[f].isna().sum()), missing_pct=frame[f].isna().mean() * 100, minimum=frame[f].min(), maximum=frame[f].max(), distinct=frame[f].nunique(), n=int(frame[f].notna().sum())) for f in features])

def grouped(frame, group):
    """Trung bình mục tiêu và số quan sát theo nhóm, không dùng Pearson mã chu kỳ."""
    result = frame.groupby(group, observed=True).traffic_volume.agg(mean='mean', median='median', n='size').reset_index()
    result['small_group'] = result.n.lt(MIN_GROUP)
    return result

def binary_effect(frame, feature, reps=BOOTSTRAPS):
    """Bootstrap khối 7 ngày lịch cho chênh trung bình nhóm 1 trừ nhóm 0."""
    z = frame[['date_time', 'traffic_volume', feature]].dropna().copy()
    g = z.groupby(feature).traffic_volume.agg(['size', 'mean'])
    n0 = int(g.loc[0, 'size']) if 0 in g.index else 0
    n1 = int(g.loc[1, 'size']) if 1 in g.index else 0
    delta = float(g.loc[1, 'mean'] - g.loc[0, 'mean']) if n0 and n1 else np.nan
    z['day'] = z.date_time.dt.normalize()
    dates = pd.date_range(z.day.min(), z.day.max(), freq='D')
    daily = []
    for flag in [0, 1]:
        agg = z.loc[z[feature].eq(flag)].groupby('day').traffic_volume.agg(['sum', 'size']).reindex(dates, fill_value=0)
        daily.extend([agg['sum'].to_numpy(), agg['size'].to_numpy()])
    rng = np.random.default_rng(SEED)
    estimates = []
    block = min(BLOCK_DAYS, len(dates))
    for _ in range(reps):
        starts = rng.integers(0, len(dates) - block + 1, size=int(np.ceil(len(dates) / block)))
        indices = (starts[:, None] + np.arange(block)).ravel()[:len(dates)]
        sum0, count0, sum1, count1 = [x[indices].sum() for x in daily]
        if count0 and count1:
            estimates.append(sum1 / count1 - sum0 / count0)
    low, high = np.quantile(estimates, [0.025, 0.975]) if len(estimates) >= reps // 2 else (np.nan, np.nan)
    return dict(feature=feature, n0=n0, n1=n1, mean_difference=delta, ci_low=low, ci_high=high, bootstrap_valid=len(estimates), small_group=min(n0, n1) < MIN_GROUP, n=n0 + n1)

def continuous_relation(frame, features):
    """Tương quan Pearson/Spearman với target cho biến liên tục hoặc lag."""
    result = []
    for col in features:
        pair = frame[[col, 'traffic_volume']].dropna()
        varies = len(pair) > 2 and pair[col].nunique() > 1
        result.append(dict(feature=col, Pearson=pair[col].corr(pair.traffic_volume) if varies else np.nan, Spearman=pair[col].corr(pair.traffic_volume, method='spearman') if varies else np.nan, n=len(pair)))
    return pd.DataFrame(result)

def binned(frame, feature):
    """Trung bình theo bin; tách 0 nếu biến tập trung ở 0 để tránh bin vô ích."""
    z = frame[[feature, 'traffic_volume']].dropna().copy()
    if z[feature].nunique() < 2:
        return pd.DataFrame([dict(bin='hằng', feature=feature, mean=z.traffic_volume.mean(), small_group=len(z) < MIN_GROUP, n=len(z))])
    format_interval = lambda interval: f'({interval.left:.2f}, {interval.right:.2f}]'
    if z[feature].eq(0).mean() > 0.5 and z[feature].ge(0).all():
        positive = z[feature].gt(0)
        z['bin'] = '0'
        if z.loc[positive, feature].nunique() > 1:
            bins = pd.qcut(z.loc[positive, feature], q=4, duplicates='drop', precision=2)
            labels = [format_interval(interval) for interval in bins.cat.categories]
            z.loc[positive, 'bin'] = bins.map(format_interval).astype(str)
        else:
            labels = ['> 0']
            z.loc[positive, 'bin'] = '> 0'
        z['bin'] = pd.Categorical(z.bin, categories=['0'] + labels, ordered=True)
    else:
        bins = pd.qcut(z[feature], q=6, duplicates='drop', precision=2)
        z['bin'] = bins.cat.rename_categories(format_interval)
    result = z.groupby('bin', observed=True).traffic_volume.agg(mean='mean', n='size').reset_index().assign(feature=feature)
    result['small_group'] = result.n.lt(MIN_GROUP)
    return result

def correlation_and_vif(frame, features):
    """VIF = 1/(1-R²) từ hồi quy mỗi X lên các X khác, có hệ số chặn.

    Dùng complete cases, chuẩn hóa chỉ để ổn định số; biến hằng có VIF không xác định.
    Không bỏ biến tự động vì VIF cao, đặc biệt với cây hoặc feature dẫn xuất.
    """
    x = frame[features].dropna().astype(float)
    corr = x.corr()
    rows = []
    for f in features:
        if x[f].nunique() < 2:
            value = np.nan
            note = 'hằng; VIF không xác định'
        else:
            y = (x[f] - x[f].mean()).to_numpy()
            others = x.drop(columns=f)
            others = others.loc[:, others.nunique().gt(1)]
            standardized = (others - others.mean()) / others.std(ddof=0)
            design = np.column_stack([np.ones(len(x)), standardized.to_numpy()])
            residual = y - design @ np.linalg.lstsq(design, y, rcond=None)[0]
            denominator = float(y @ y)
            fraction = float(residual @ residual) / denominator
            value = np.inf if fraction < 1e-10 else 1 / fraction
            note = 'đa cộng tuyến tuyến tính' if value > 5 else 'chưa vượt ngưỡng mô tả 5'
        rows.append(dict(feature=f, VIF=value, note=note, n=len(x)))
    return (corr, pd.DataFrame(rows))

def matched_holidays(train):
    """So lễ với ngày thường cùng thứ/giờ; bootstrap theo ngày sự kiện."""
    normal = train.loc[train.is_holiday.eq(0)].groupby(['day_of_week', 'hour']).traffic_volume.agg(normal_mean='mean', n0='size')
    holiday = train.loc[train.is_holiday.eq(1)].join(normal, on=['day_of_week', 'hour'])
    holiday['difference'] = holiday.traffic_volume - holiday.normal_mean
    result = holiday.groupby(['day_of_week', 'hour']).agg(holiday_mean=('traffic_volume', 'mean'), normal_mean=('normal_mean', 'mean'), difference=('difference', 'mean'), n0=('n0', 'first'), n=('difference', 'count')).reset_index()
    result['small_group'] = result.n.lt(MIN_GROUP)
    daily = holiday.groupby(holiday.date_time.dt.normalize()).difference.agg(['sum', 'count'])
    rng = np.random.default_rng(SEED)
    sample = rng.integers(0, len(daily), size=(BOOTSTRAPS, len(daily)))
    estimates = daily['sum'].to_numpy()[sample].sum(axis=1) / daily['count'].to_numpy()[sample].sum(axis=1)
    summary = dict(difference=holiday.difference.mean(), low=float(np.quantile(estimates, 0.025)), high=float(np.quantile(estimates, 0.975)), n=len(holiday), n_days=len(daily))
    return (result, summary)

def acf_pairs(train, max_lag=168):
    """ACF theo cặp giờ hợp lệ: corr(y(t), y(t-k)), giữ gaps và báo n mỗi k.

    Đây là ACF chuẩn hóa theo cặp, không nối chuỗi bằng cách bỏ giờ thiếu.
    Các lag có tập cặp khác nhau; không gắn dải tin cậy white-noise mặc định.
    """
    series = train.set_index('date_time').traffic_volume
    rows = []
    for k in range(max_lag + 1):
        past = pd.Series(series.reindex(series.index - pd.Timedelta(hours=k)).to_numpy(), index=series.index)
        pair = pd.concat([series.rename('now'), past.rename('past')], axis=1).dropna()
        rows.append(dict(lag_hours=k, ACF=pair['now'].corr(pair.past), n=len(pair)))
    return pd.DataFrame(rows)

def stability(frame, features):
    """Độ ổn định theo năm train, bao gồm n và tỷ lệ thiếu."""
    rows = []
    for year, part in frame.groupby(frame.date_time.dt.year):
        for f in features:
            rows.append(dict(year=year, feature=f, mean=part[f].mean(), missing_pct=part[f].isna().mean() * 100, n=int(part[f].notna().sum())))
    return pd.DataFrame(rows)



def figure(ctx, letter, number, slug, fig, title, reading):
    """Lưu PNG và in lời hướng dẫn ngay dưới biểu đồ trong notebook."""
    fig.suptitle(title, fontsize=14, wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = ctx['figures'] / f'eda_{letter}_{number:02d}_{slug}.png'
    fig.savefig(path, bbox_inches='tight')
    plt.show()
    plt.close(fig)
    say(f'{reading}')

def binary_plot(ctx, letter, results, number):
    """Đồ thị chênh trung bình và CI, không trình bày hệ số như nhân quả."""
    z = results.dropna(subset=['ci_low', 'ci_high'])
    fig, ax = plt.subplots(figsize=(10, max(3, len(z) * 0.35)))
    if len(z):
        ax.hlines(np.arange(len(z)), z.ci_low, z.ci_high, color='#207E8D')
        ax.scatter(z.mean_difference, np.arange(len(z)), color='#103451')
        ax.set_yticks(np.arange(len(z)), z.feature)
    ax.axvline(0, color='grey', linestyle='--')
    ax.set(xlabel='Chênh trung bình nhóm 1 - nhóm 0 (xe/giờ)', ylabel='Cờ nhị phân')
    negative = int(results.ci_high.lt(0).sum())
    positive = int(results.ci_low.gt(0).sum())
    figure(ctx, letter, number, 'binary_ci', fig, f'CI mô tả: {positive} cờ lệch dương, {negative} cờ lệch âm so với 0', 'Điểm là chênh trung bình, đoạn ngang là CI bootstrap khối 7 ngày 95%. Đọc cùng n0/n1; nhóm quá ít mẫu hoặc không có biến thiên không cho CI đáng tin cậy. Chênh này chưa điều chỉnh lịch và không chứng minh tác động nhân quả.')

def corr_plot(ctx, letter, matrix, number, n):
    fig, ax = plt.subplots(figsize=(max(8, len(matrix) * 0.32), max(6, len(matrix) * 0.29)))
    sns.heatmap(matrix, vmin=-1, vmax=1, center=0, cmap='vlag', ax=ax)
    ax.set(xlabel='Đặc trưng (đơn vị khác nhau)', ylabel='Đặc trưng (đơn vị khác nhau)')
    figure(ctx, letter, number, 'feature_corr', fig, f'Một số feature dẫn xuất cùng nguồn chia sẻ thông tin; n={n:,} giờ đầy đủ', 'Màu thể hiện Pearson giữa các feature, không dùng để đánh giá liên hệ của mã giờ/thứ/tháng thô với target. Ô trống là hệ số không xác định, thường do biến hằng; không tự bỏ feature chỉ từ hình này.')



