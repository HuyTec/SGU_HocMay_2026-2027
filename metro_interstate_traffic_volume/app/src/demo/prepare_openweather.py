"""Prepare weather-only data with explicit optional-precipitation provenance.

OpenWeather FAQ says omitted phenomena did not occur. Apply that interpretation
only when the weather labels/codes and alternative accumulations do not conflict.
Raw API pages and the availability CSV remain unchanged. No traffic time join.
"""

from collections import Counter
from datetime import datetime, timezone
import json
import pandas as pd

from .download_openweather import FOLDER, START, END

FAQ = 'https://openweathermap.org/faq#api'
KNOWN = {'Clear', 'Clouds', 'Drizzle', 'Fog', 'Haze', 'Mist', 'Rain',
         'Smoke', 'Snow', 'Squall', 'Thunderstorm'}


def precipitation(row, kind):
    """Distinguish actual 1h values, documented non-events, and conflicts."""
    obj = row.get(kind)
    if isinstance(obj, dict) and obj.get('1h') is not None:
        return obj['1h'], 'api_1h'
    weather = row.get('weather') or []
    names = {w.get('main') for w in weather}
    codes = {w.get('id') for w in weather}
    indicated = (bool(names & {'Rain', 'Drizzle', 'Thunderstorm'}) or bool(codes & {615, 616})) if kind == 'rain' else 'Snow' in names
    if kind in row or indicated or not weather:
        return None, 'unresolved_missing_or_conflict'
    return 0.0, 'zero_by_provider_omission_rule'


def main():
    """Validate the complete archive and write a separate prepared weather CSV."""
    manifest = json.loads((FOLDER / 'download_manifest.json').read_text())
    raw = [r for p in manifest for r in json.loads((FOLDER / p['file']).read_text())['data']
           if START <= r['dt'] < END]
    raw.sort(key=lambda r: r['dt'])
    assert [r['dt'] for r in raw] == list(range(START, END, 3600))
    rows = []
    for r in raw:
        rain, rain_status = precipitation(r, 'rain')
        snow, snow_status = precipitation(r, 'snow')
        names = sorted({w['main'] for w in r.get('weather', [])})
        rows.append({'date_time_utc': datetime.fromtimestamp(r['dt'], timezone.utc).isoformat(),
                     'temp': r.get('temp'), 'rain_1h': rain, 'snow_1h': snow,
                     'clouds_all': r.get('clouds'), 'weather_main': '|'.join(names),
                     'weather_main_json': json.dumps(names),
                     'rain_1h_status': rain_status, 'snow_1h_status': snow_status})
    frame = pd.DataFrame(rows)
    assert frame.date_time_utc.is_unique
    for column in ['temp', 'rain_1h', 'snow_1h', 'clouds_all']:
        values = pd.to_numeric(frame[column], errors='raise')
        assert values.dropna().ge(0).all(), column
    assert frame.clouds_all.dropna().le(100).all()
    labels = {w['main'] for r in raw for w in r.get('weather', [])}
    audit = {'hours': len(frame), 'missing_values': frame.isna().sum().to_dict(),
             'rain_status_counts': dict(Counter(frame.rain_1h_status)),
             'snow_status_counts': dict(Counter(frame.snow_1h_status)),
             'unknown_weather_labels': sorted(labels - KNOWN),
             'positive_rain_hours': int(frame.rain_1h.gt(0).sum()),
             'positive_snow_hours': int(frame.snow_1h.gt(0).sum()),
             'rule_source': FAQ,
             'time_policy': 'UTC retained; no fixed-CST/DST choice or traffic join',
             'unit_policy': 'temp Kelvin, clouds %, rain/snow mm/h as returned by API',
             'model_status': 'weather prepared only; no inference/training or UCI replacement'}
    frame.to_csv(FOLDER / 'openweather_2018_weather_prepared.csv', index=False)
    (FOLDER / 'preparation_audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
