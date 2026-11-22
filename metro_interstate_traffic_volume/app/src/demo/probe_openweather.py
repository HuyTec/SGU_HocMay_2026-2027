"""Fetch one historical page for inspection; never fit, predict or paginate.

Set OPENWEATHER_API_KEY in the process environment, then run from project root:
python -m app.src.demo.probe_openweather
The regional coordinates are provisional, not a verified UCI weather location.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


ENDPOINT = 'https://api.openweathermap.org/data/4.0/onecall/timeline/1h'
OUTPUT = Path(__file__).resolve().parents[3] / 'data/external/mndot/weather/openweather_probe'


def main():
    """Make at most one request, saving data without credential-bearing links."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', default='2018-11-01T00:00:00+00:00')
    parser.add_argument('--lat', type=float, default=44.95)
    parser.add_argument('--lon', type=float, default=-93.15)
    args = parser.parse_args()
    start = datetime.fromisoformat(args.start.replace('Z', '+00:00'))
    if start.tzinfo is None:
        parser.error('--start must include a UTC offset')
    if not (-90 <= args.lat <= 90 and -180 <= args.lon <= 180):
        parser.error('invalid coordinates')
    key = os.environ.get('OPENWEATHER_API_KEY', '').strip()
    if not key:
        print('NOT_REQUESTED: set OPENWEATHER_API_KEY; One Call subscription must be active.')
        return 2
    params = dict(lat=args.lat, lon=args.lon, start=int(start.timestamp()), units='standard')
    url = ENDPOINT + '?' + urlencode({**params, 'appid': key})
    try:
        with urlopen(url, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as exc:
        # Never print exception URLs/body: they may echo the key.
        hints = {401: 'Check key activation and One Call subscription.',
                 429: 'Quota reached; no retry performed.'}
        print(f'HTTP {exc.code}: {hints.get(exc.code, "Request rejected; no retry performed.")}')
        return 1
    except (URLError, TimeoutError, ValueError):
        print('NETWORK_OR_JSON_ERROR: no retry performed; credentials omitted.')
        return 1
    rows = payload.get('data') if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) for r in rows):
        print('UNEXPECTED_RESPONSE: no historical records verified.')
        return 1
    # Pagination URLs contain appid. Keep only whether pagination exists.
    page = {k: v for k, v in payload.items() if k not in ('next', 'prev')}
    serialized = json.dumps(page, ensure_ascii=False, indent=2)
    if key in serialized:
        print('CREDENTIAL_IN_RESPONSE: refusing to save response.')
        return 1
    content = serialized.encode('utf-8')
    summary = {
        'endpoint': ENDPOINT, 'parameters_without_key': params,
        'retrieved_utc': datetime.now(timezone.utc).isoformat(),
        'coordinate_status': 'provisional regional point, not verified UCI weather location',
        'requests': 1, 'rows': len(rows), 'pagination_not_followed': bool(payload.get('next')),
        'sha256_saved_response': hashlib.sha256(content).hexdigest(),
        'first_dt': rows[0].get('dt'), 'last_dt': rows[-1].get('dt'),
        'field_present_counts': {field: sum(row.get(field) is not None for row in rows)
                                 for field in ('dt', 'temp', 'clouds', 'weather')},
        'rain_1h_present': sum(isinstance(r.get('rain'), dict) and r['rain'].get('1h') is not None for r in rows),
        'snow_1h_present': sum(isinstance(r.get('snow'), dict) and r['snow'].get('1h') is not None for r in rows),
        'missing_precipitation_policy': 'preserved absent; not filled with zero',
        'usage': 'source inspection only; no traffic join or model scoring',
    }
    folder = OUTPUT / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder.mkdir(parents=True)
    (folder / 'response_without_pagination_links.json').write_bytes(content)
    (folder / 'inspection_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('Saved:', folder)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
