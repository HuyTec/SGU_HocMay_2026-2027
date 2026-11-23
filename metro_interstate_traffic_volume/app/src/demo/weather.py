"""Validated OpenWeather loading and explicit time-policy preview joins.

Joins affect post-UCI weather only. Traffic, holiday and UCI context are never
filled or overwritten. Time-policy previews do not certify model compatibility.
"""

from datetime import timezone, timedelta
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

FOLDER = Path(__file__).resolve().parents[3] / 'data/external/mndot/weather/openweather_2018'
PREPARED = FOLDER / 'openweather_2018_weather_prepared.csv'
RAW = FOLDER / 'openweather_2018_hourly.csv'
AUDIT = FOLDER / 'preparation_audit.json'
SUMMARY = FOLDER / 'inspection_summary.json'
POLICIES = ['CST cố định · UTC−06:00', 'America/Chicago · có DST']
VALUES = ['temp', 'rain_1h', 'snow_1h', 'clouds_all', 'weather_main']
KNOWN = {'clear', 'clouds', 'drizzle', 'fog', 'haze', 'mist', 'rain',
         'smoke', 'snow', 'squall', 'thunderstorm'}


def load():
    """Validate against sanitized raw records, including omission provenance."""
    summary = json.loads(SUMMARY.read_text(encoding='utf-8'))
    if hashlib.sha256(RAW.read_bytes()).hexdigest() != summary['csv_sha256']:
        raise ValueError('Hash weather OpenWeather gốc thay đổi.')
    frame, raw = pd.read_csv(PREPARED), pd.read_csv(RAW)
    required = {'date_time_utc', *VALUES, 'weather_main_json', 'rain_1h_status', 'snow_1h_status'}
    if not required <= set(frame):
        raise ValueError('OpenWeather thiếu schema chuẩn hóa.')
    times = pd.to_datetime(frame.date_time_utc, utc=True, errors='raise')
    expected = pd.date_range(summary['start_inclusive_utc'], summary['end_inclusive_utc'], freq='h')
    if list(times) != list(expected) or len(frame) != summary['hours'] or not times.is_unique:
        raise ValueError('Weather thiếu/trùng/lệch giờ.')
    if len(raw) != len(frame) or not frame.date_time_utc.equals(raw.date_time_utc):
        raise ValueError('Weather chuẩn hóa không khớp giờ bản gốc.')
    for name, origin in [('temp', 'temp_k'), ('clouds_all', 'clouds_all')]:
        if not frame[name].equals(raw[origin]):
            raise ValueError(f'Weather chuẩn hóa thay đổi {name}.')
    normalized = []
    for names in frame.weather_main_json.map(json.loads):
        labels = [n.lower() for n in names]
        if not labels or set(labels) - KNOWN:
            raise ValueError('Nhãn OpenWeather trống hoặc ngoài C30.')
        normalized.append(' | '.join(sorted(set(labels))))
    if not frame.weather_main_json.equals(raw.weather_main_json):
        raise ValueError('Nhãn weather khác bản gốc.')
    frame['weather_main'] = normalized
    for kind in ['rain', 'snow']:
        col = kind + '_1h'
        status = frame[col + '_status']
        actual = status.eq('api_1h')
        zeros = status.eq('zero_by_provider_omission_rule')
        if not (actual | zeros).all() or not raw[col + '_present'].equals(actual):
            raise ValueError(f'Provenance {col} không khớp.')
        if not np.allclose(frame.loc[actual, col], raw.loc[actual, col]) or not frame.loc[zeros, col].eq(0).all():
            raise ValueError(f'Giá trị {col} khác bản gốc/quy tắc.')
        event = frame.weather_main.str.contains('snow' if kind == 'snow' else 'rain|drizzle|thunderstorm')
        if (zeros & event).any():
            raise ValueError(f'{col} có nhãn mâu thuẫn với quy tắc zero.')
    numbers = frame[['temp', 'rain_1h', 'snow_1h', 'clouds_all']]
    if not np.isfinite(numbers).all().all() or numbers.lt(0).any().any() or frame.clouds_all.gt(100).any():
        raise ValueError('Weather chứa giá trị vật lý không hợp lệ.')
    frame['date_time_utc'] = times
    return frame


def utc_for_wall(times, policy):
    """Keep ambiguous/nonexistent Chicago hours unresolved rather than guessing."""
    if policy not in POLICIES:
        raise ValueError('Chính sách thời gian không được hỗ trợ.')
    zone = timezone(timedelta(hours=-6)) if policy == POLICIES[0] else 'America/Chicago'
    return pd.DatetimeIndex(times).tz_localize(zone, ambiguous='NaT', nonexistent='NaT').tz_convert('UTC')


def attach_preview(context, weather, uci_end, policy):
    """Attach weather to actual post-UCI records; never synthesize traffic hours."""
    result = context.copy()
    external = result.date_time.gt(pd.Timestamp(uci_end))
    part = result.loc[external, ['date_time']].copy()
    part['date_time_utc'] = utc_for_wall(part.date_time, policy)
    joined = part.merge(weather, on='date_time_utc', how='left', validate='many_to_one', indicator=True)
    for col in [*VALUES, 'date_time_utc', 'rain_1h_status', 'snow_1h_status']:
        result.loc[external, col] = joined[col].to_numpy()
    result.loc[external, 'weather_time_policy'] = policy
    result.loc[external, 'weather_source'] = 'OpenWeather One Call 4.0 · ghép xem trước'
    result.loc[~external, 'weather_source'] = 'UCI gốc'
    result.loc[external, 'weather_join_status'] = np.where(
        joined.date_time_utc.isna(), 'Giờ DST mơ hồ/không tồn tại',
        np.where(joined['_merge'].eq('both'), 'Đã ghép theo giả định', 'Ngoài độ phủ weather'))
    return result


def compare(uci, weather, policy):
    """Compare weather values on common hours without model/target scoring."""
    old = uci.loc[uci.date_time.dt.year.eq(2018), ['date_time', *VALUES]].copy()
    old['date_time_utc'] = utc_for_wall(old.date_time, policy)
    joined = old.merge(weather, on='date_time_utc', how='inner', suffixes=('_uci', '_ow'), validate='many_to_one')
    summary = []
    for col in VALUES[:-1]:
        valid = np.isfinite(joined[col + '_uci']) & np.isfinite(joined[col + '_ow'])
        difference = joined.loc[valid, col + '_ow'] - joined.loc[valid, col + '_uci']
        joined[col + '_difference'] = joined[col + '_ow'] - joined[col + '_uci']
        summary.append({'Biến': col, 'Giờ có cả hai': int(valid.sum()),
                        'Lệch trung bình OW − UCI': difference.mean(),
                        'Sai khác tuyệt đối TB': difference.abs().mean(),
                        'RMSE giữa nguồn': np.sqrt((difference ** 2).mean())})
    same = joined.weather_main_uci.map(lambda s: set(str(s).lower().split(' | '))).eq(
        joined.weather_main_ow.map(lambda s: set(s.split(' | '))))
    return {'rows': joined, 'summary': pd.DataFrame(summary), 'policy': policy,
            'label_equal': int(same.sum()), 'n': len(joined),
            'unresolved_dst_uci': int(old.date_time_utc.isna().sum())}
