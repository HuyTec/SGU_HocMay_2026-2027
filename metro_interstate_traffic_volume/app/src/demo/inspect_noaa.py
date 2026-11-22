"""Inspect downloaded NOAA ISD CSVs without joining traffic or building C30.

Run from the project root with ``python -m app.src.demo.inspect_noaa``.
Availability means a field exists and is not its documented missing sentinel;
it does not certify quality, physical equivalence, or hourly alignment.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path

import pandas as pd

from .service import MNDOT

FOLDER = MNDOT / 'weather/noaa'


def inspect_station(path):
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    times = pd.to_datetime(raw.DATE, utc=True, errors='raise')
    periods = pd.date_range('2018-01-01', '2018-12-31 23:00', freq='h', tz='UTC')
    hourly = times.dt.floor('h')
    window = times.ge(pd.Timestamp('2018-10-01', tz='UTC')) & times.lt(pd.Timestamp('2018-12-13', tz='UTC'))
    weather_columns = [c for c in raw if c.startswith(('AW', 'AU', 'MW', 'AY', 'AZ'))]
    weather_present = raw[weather_columns].ne('').any(axis=1) if weather_columns else pd.Series(False, index=raw.index)
    temp = raw.TMP.str.split(',', expand=True)
    finite_temp = temp[0].ne('+9999') & pd.to_numeric(temp[0], errors='coerce').notna()
    precipitation = []
    for column in ['AA1', 'AA2', 'AA3', 'AA4']:
        if column not in raw:
            continue
        values = raw[column].str.split(',', expand=True).reindex(columns=range(4))
        valid = raw[column].ne('') & values[0].ne('99') & values[1].ne('9999')
        valid &= pd.to_numeric(values[1], errors='coerce').notna()
        one_hour = valid & values[0].eq('01')
        qc_screen = one_hour & values[3].isin(['1', '5']) & values[2].isin(['9', '2'])
        precipitation.append({'field': column, 'rows_present': int(raw[column].ne('').sum()),
                              'nonmissing_amount_by_period_hours': dict(Counter(values.loc[valid, 0])),
                              'one_hour_amount_rows': int((valid & values[0].eq('01')).sum()),
                              'one_hour_unique_utc_hour_buckets': int(hourly[valid & values[0].eq('01')].nunique()),
                              'one_hour_condition_codes': dict(Counter(values.loc[one_hour, 2].dropna())),
                              'one_hour_qc_1_or_5_and_condition_9_or_2_hour_buckets': int(hourly[qc_screen].nunique()),
                              'window_one_hour_qc_1_or_5_and_condition_9_or_2_hour_buckets': int(hourly[window & qc_screen].nunique()),
                              'condition_codes': dict(Counter(values.loc[valid, 2].dropna())),
                              'quality_codes': dict(Counter(values.loc[valid, 3].dropna()))})
    summary = {
        'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'station_ids': sorted(raw.STATION.unique().tolist()), 'station_names': sorted(raw.NAME.unique().tolist()),
        'coordinates_in_file': raw[['LATITUDE', 'LONGITUDE']].drop_duplicates().to_dict('records'),
        'rows': len(raw), 'start_utc': str(times.min()), 'end_utc': str(times.max()),
        'report_types': raw.REPORT_TYPE.value_counts().to_dict(),
        'routine_fm15_unique_utc_hour_buckets': int(hourly[raw.REPORT_TYPE.str.strip().eq('FM-15')].nunique()),
        'expected_utc_hours_2018': len(periods), 'utc_hour_buckets_with_any_report': int(hourly.nunique()),
        'missing_utc_hour_buckets_2018': int(len(periods.difference(hourly))),
        'duplicate_exact_timestamps_rows_beyond_first': int(times.duplicated().sum()),
        'records_not_at_start_of_hour': int(times.ne(hourly).sum()),
        'hour_buckets_with_multiple_reports': int(hourly.value_counts().gt(1).sum()),
        'temperature_nonmissing_rows_before_qc': int(finite_temp.sum()),
        'temperature_quality_codes': temp[1].value_counts().to_dict(),
        'precipitation_groups': precipitation,
        'cloud_and_snow_groups_present': {c: int(raw[c].ne('').sum()) for c in raw if c.startswith(('GA', 'GD', 'GF', 'AJ', 'AL'))},
        'weather_groups_present': {c: int(raw[c].ne('').sum()) for c in weather_columns},
        'rows_with_weather_group': int(weather_present.sum()),
        'utc_inspection_window': '2018-10-01 00:00Z <= t < 2018-12-13 00:00Z; NOT a traffic/timezone join',
        'window_rows': int(window.sum()), 'window_utc_hour_buckets': int(hourly[window].nunique()),
        'window_temperature_nonmissing_hour_buckets': int(hourly[window & finite_temp].nunique()),
        'warning': 'No resampling, report selection, quality acceptance, timezone join or C30 compatibility has been approved.',
    }
    raw.loc[window, [c for c in ['STATION', 'DATE', 'REPORT_TYPE', 'NAME', 'TMP', 'AA1', 'AA2',
                                'GF1', 'GA1', 'GD1', 'AJ1', 'AL1', 'AW1', 'AU1', 'MW1'] if c in raw]].head(200).to_csv(
        FOLDER / f'{path.stem}_raw_preview.csv', index=False)
    return summary


def main():
    manifest = json.loads((FOLDER / 'download_manifest.json').read_text(encoding='utf-8'))
    results = []
    for source in manifest['files']:
        path = FOLDER / source['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f'File hash mismatch: {path.name}')
        results.append(inspect_station(path))
    (FOLDER / 'inspection_summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    for result in results:
        print(result['station_names'], result['rows'], 'rows;', result['utc_hour_buckets_with_any_report'], 'UTC hour buckets')
        print('precipitation:', result['precipitation_groups'])
        print('cloud/snow:', result['cloud_and_snow_groups_present'])
        print('weather:', result['weather_groups_present'])


if __name__ == '__main__':
    main()
