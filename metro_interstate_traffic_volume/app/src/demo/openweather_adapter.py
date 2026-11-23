"""Explicit mixed-source historical simulation; never replace UCI weather.

Flow: verified weather CSV -> fixed UTC-6 demo clock -> one-to-one traffic join
-> federal holiday calendar -> original UCI context + post-UCI external rows.
These declared simulation policies are not proof of the original weather clock,
location or event calendar. Do not interpret results as operational forecasting.
"""

import json
import hashlib
from pathlib import Path
import pandas as pd
from src.data import federal_holidays

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT / 'data/external/mndot/weather/openweather_2018'
PREPARED = FOLDER / 'openweather_2018_weather_prepared.csv'
RAW = FOLDER / 'openweather_2018_hourly.csv'
AUDIT = FOLDER / 'inspection_summary.json'
PREPARATION = FOLDER / 'preparation_audit.json'
SOURCE = 'MnDOT + OpenWeather · mô phỏng CST'
POLICY = ('Mô phỏng lịch sử: UTC−6 cố định theo cách diễn đạt CST của UCI; '
          'chưa xác minh clock MnDOT/DST. Ngày lễ dùng lịch liên bang Mỹ (ngày nghỉ bù), '
          'gắn mọi giờ trong ngày; chưa tái tạo toàn bộ sự kiện UCI. '
          'Weather tại điểm khu vực người dùng chọn; dùng cùng giờ, chưa biết trước lúc dự báo.')


def load_weather():
    """Check prepared values against the hashed availability-preserving CSV."""
    meta = json.loads(AUDIT.read_text(encoding='utf-8'))
    if hashlib.sha256(RAW.read_bytes()).hexdigest() != meta['csv_sha256']:
        raise ValueError('Hash OpenWeather gốc không khớp audit.')
    raw = pd.read_csv(RAW)
    weather = pd.read_csv(PREPARED)
    times = pd.to_datetime(weather.date_time_utc, utc=True)
    if len(weather) != meta['hours'] or not times.is_unique or not times.diff().dropna().eq(pd.Timedelta(hours=1)).all():
        raise ValueError('OpenWeather thiếu hoặc trùng giờ.')
    if not weather.date_time_utc.equals(raw.date_time_utc):
        raise ValueError('Timestamp weather chuẩn hóa khác bản gốc.')
    for column, original in [('temp', 'temp_k'), ('clouds_all', 'clouds_all')]:
        if not weather[column].equals(raw[original]):
            raise ValueError(f'{column} khác bản gốc.')
    if weather[['temp', 'rain_1h', 'snow_1h', 'clouds_all', 'weather_main']].isna().any().any():
        raise ValueError('Weather chuẩn hóa còn thiếu; không dùng imputer để che lỗi adapter.')
    known = {'clear','clouds','drizzle','fog','haze','mist','rain','smoke','snow','squall','thunderstorm'}
    for i, row in weather.iterrows():
        names = json.loads(raw.weather_main_json.iloc[i])
        if set(row.weather_main.lower().split('|')) != {n.lower() for n in names} or not {n.lower() for n in names} <= known:
            raise ValueError('Nhãn weather khác bản gốc hoặc ngoài C30.')
    for kind in ['rain', 'snow']:
        column = kind + '_1h'
        present = raw[column + '_present'].eq(True)
        status = weather[column + '_status']
        if not weather.loc[present, column].equals(raw.loc[present, column]):
            raise ValueError(f'{column} đo/tính trực tiếp khác bản gốc.')
        if not status[present].eq('api_1h').all() or not status[~present].eq('zero_by_provider_omission_rule').all() or not weather.loc[~present,column].eq(0).all():
            raise ValueError(f'{column} không đúng chính sách chuẩn hóa.')
    weather['date_time'] = times.dt.tz_convert('Etc/GMT+6').dt.tz_localize(None)
    weather['weather_main'] = weather.weather_main.str.lower().str.replace('|', ' | ', regex=False)
    return weather


def join_sources(context, traffic, weather):
    """Only enrich post-UCI rows; retain context, targets and missing hours."""
    from .service import FIELDS
    uci_end = context.loc[context.source.eq('UCI context'), 'date_time'].max()
    columns = ['date_time', 'date_time_utc', 'temp', 'rain_1h', 'snow_1h', 'clouds_all',
               'weather_main', 'rain_1h_status', 'snow_1h_status']
    merged = traffic[['date_time', 'traffic_volume']].merge(weather[columns], how='left', on='date_time', validate='one_to_one')
    if merged[columns[1:]].isna().any().any():
        raise ValueError('Không đủ weather cho traffic sau UCI.')
    dates = merged.date_time.dt.normalize()
    holidays = federal_holidays(dates.min(), dates.max())
    merged['is_holiday'] = dates.isin(holidays.index).astype('int8')
    merged['holiday_name'] = dates.map(holidays).fillna('None')
    merged['holiday_source'] = 'USFederalHolidayCalendar observed dates · simulation policy'
    merged['weather_source'] = 'OpenWeather One Call 4.0'
    merged['clock_policy'] = 'fixed UTC-6 · historical simulation assumption'
    merged['source'] = SOURCE
    if not merged.date_time.gt(uci_end).all():
        raise ValueError('Không được thay weather UCI bằng adapter ngoài.')
    full = pd.concat([context.loc[context.date_time.le(uci_end)].copy(), merged], ignore_index=True).sort_values('date_time')
    if not full.date_time.is_unique or not set(FIELDS) <= set(full):
        raise ValueError('Bảng tích hợp không đạt schema theo giờ.')
    return full, merged


def compare_uci(weather, uci):
    """Compare input weather on overlap only, without traffic/model scores."""
    joined = uci.merge(weather, on='date_time', suffixes=('_uci', '_new'), validate='one_to_one')
    rows = []
    for col in ['temp', 'rain_1h', 'snow_1h', 'clouds_all']:
        valid = joined[[col+'_uci', col+'_new']].dropna()
        diff = valid[col+'_new'] - valid[col+'_uci']
        rows.append({'Biến':col, 'Số giờ đối chiếu':len(valid), 'Độ lệch trung bình':diff.mean(),
                     'Sai khác tuyệt đối TB':diff.abs().mean(), 'Tỷ lệ bằng nhau (%)':diff.eq(0).mean()*100})
    plot = joined[['date_time','temp_uci','temp_new']].copy()
    return pd.DataFrame(rows), plot
