"""Download a bounded, resumable historical weather archive without model work.

Flow: fixed UTC windows -> cached API pages -> coverage validation -> CSV + audit.
Missing precipitation remains missing. Keys and pagination URLs are never saved.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from .probe_openweather import ENDPOINT

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT / 'data/external/mndot/weather/openweather_2018'
START = int(datetime(2018, 1, 1, tzinfo=timezone.utc).timestamp())
END = int(datetime(2018, 12, 13, tzinfo=timezone.utc).timestamp())
PARAMS = {'lat': 44.951424, 'lon': -93.147145, 'units': 'standard'}


def get_page(start, key):
    """Fetch one fixed window unless its validated cache is already present."""
    path = FOLDER / 'pages' / f'{start}.json'
    if path.exists():
        return start, json.loads(path.read_text(encoding='utf-8')), False
    url = ENDPOINT + '?' + urlencode({**PARAMS, 'start': start, 'appid': key})
    try:
        with urlopen(url, timeout=35) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f'HTTP {exc.code}; no automatic retry') from None
    except Exception:
        raise RuntimeError('Network/JSON failure; credentials omitted; rerun to resume') from None
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise RuntimeError('Invalid page schema')
    rows = payload['data']
    expected = list(range(start, start + 20 * 3600, 3600))
    if [r.get('dt') for r in rows] != expected:
        raise RuntimeError(f'Unexpected timestamps in page {start}')
    payload = {k: v for k, v in payload.items() if k not in ('next', 'prev')}
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    if key in content:
        raise RuntimeError('Credential echoed in response; refusing persistence')
    path.write_text(content, encoding='utf-8')
    return start, payload, True


def main():
    """Fetch at most 416 pages per invocation and preserve field availability."""
    key = os.environ.get('OPENWEATHER_API_KEY', '').strip()
    if not key:
        raise SystemExit('Set OPENWEATHER_API_KEY')
    starts = list(range(START, END, 20 * 3600))
    assert len(starts) <= 450
    (FOLDER / 'pages').mkdir(parents=True, exist_ok=True)
    rows, manifest, requested = [], [], 0
    # Batches of four bound in-flight requests; a rejection stops subsequent batches.
    with ThreadPoolExecutor(max_workers=4) as pool:
        for offset in range(0, len(starts), 4):
            batch = starts[offset:offset + 4]
            results = list(pool.map(lambda s: get_page(s, key), batch))
            for start, payload, fetched in results:
                requested += int(fetched)
                rows.extend(r for r in payload['data'] if START <= r['dt'] < END)
                path = FOLDER / 'pages' / f'{start}.json'
                manifest.append({'file': str(path.relative_to(FOLDER)), 'start': start,
                                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            if offset % 40 == 0 or offset + 4 >= len(starts):
                print(f'PROGRESS pages={min(offset+4,len(starts))}/{len(starts)} hours={len(rows)}', flush=True)
    rows.sort(key=lambda r: r['dt'])
    if [r['dt'] for r in rows] != list(range(START, END, 3600)):
        raise RuntimeError('Coverage validation failed; normalized CSV not written')
    output = []
    labels = Counter()
    for row in rows:
        weather = row.get('weather')
        names = sorted({w['main'] for w in weather}) if isinstance(weather, list) else []
        labels.update(names)
        rain = row.get('rain') or {}
        snow = row.get('snow') or {}
        output.append({
            'date_time_utc': datetime.fromtimestamp(row['dt'], timezone.utc).isoformat(),
            'temp_k': row.get('temp'), 'clouds_all': row.get('clouds'),
            'rain_1h': rain.get('1h'), 'snow_1h': snow.get('1h'),
            'rain_1h_present': rain.get('1h') is not None,
            'snow_1h_present': snow.get('1h') is not None,
            'weather_main_json': json.dumps(names, ensure_ascii=False),
            'weather_json': json.dumps(weather, ensure_ascii=False),
            'humidity_pct': row.get('humidity'), 'wind_speed_m_s': row.get('wind_speed'),
            'source': 'OpenWeather One Call 4.0',
        })
    csv_path = FOLDER / 'openweather_2018_hourly.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    audit = {'endpoint': ENDPOINT, 'parameters_without_key': PARAMS,
             'start_inclusive_utc': output[0]['date_time_utc'],
             'end_inclusive_utc': output[-1]['date_time_utc'],
             'hours': len(rows), 'missing_hours': 0, 'duplicate_hours': 0,
             'requests_this_invocation': requested, 'cached_pages': len(starts),
             'field_present_counts': {f: sum(r.get(f) is not None for r in rows)
                                      for f in ('temp', 'clouds', 'weather')},
             'rain_1h_present': sum(r['rain_1h_present'] for r in output),
             'snow_1h_present': sum(r['snow_1h_present'] for r in output),
             'weather_label_counts': dict(labels),
             'missing_policy': 'No zero filling, resampling, weather inference or traffic join',
             'coordinate_status': 'User-selected regional point, not verified UCI weather origin',
             'retrieved_utc': datetime.now(timezone.utc).isoformat(),
             'csv_sha256': hashlib.sha256(csv_path.read_bytes()).hexdigest()}
    (FOLDER / 'inspection_summary.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    (FOLDER / 'download_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(audit, indent=2), flush=True)


if __name__ == '__main__':
    main()
