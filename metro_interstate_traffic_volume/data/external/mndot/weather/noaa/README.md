# NOAA 2018 station audit · not normalized C30

Public NOAA Global Hourly ISD CSVs: `72658414927.csv` (KSTP) and `72658014922.csv` (KMSP).
Both were fetched without authentication or payment from the NOAA NODD AWS archive.
This is the historical ISD product, not LCDv1/v2 and not the current GHCNh product.

- `download_manifest.json`: original URLs, byte counts, SHA256, authority notice and station-inventory provenance.
- `isd-history.csv`: public NOAA station inventory, unchanged bytes.
- `nearby_stations_2018.csv`: derived candidates with distance to approximate regional point 44.95/-93.15.
- `inspection_summary.json`: report counts, UTC coverage, raw-field availability and diagnostic quality screening.
- `*_raw_preview.csv`: first 200 raw reports within the inspection window, retaining original field encoding.
- `kstp_header_excerpt.txt`: first complete lines of a separate byte-range request for schema inspection; not a full dataset.

Distance is not from a surveyed ATR301 coordinate. UTC hour buckets are only coverage diagnostics;
they are not an approved aggregation or a traffic timestamp join. Preserve duplicates, quality codes,
trace indicators and report types until a source contract is established.

Reproduce inspection from repository root:

```powershell
app/.venv/Scripts/python.exe -X utf8 -m app.src.demo.inspect_noaa
```

Read `app/docs/noaa_review.md` for results and remaining C30 incompatibilities.
