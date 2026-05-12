# WFS Extractor — OGC Web Feature Service 2.0

This extractor fetches geospatial features from OGC WFS 2.0 endpoints and
flattens the responses into tabular records for Parquet storage under
`Data/`.

## Modules

### `client.py`

Generic WFS 2.0 HTTP client. Handles:

- **`get_capabilities(base_url)`** — fetches and parses the `GetCapabilities`
  XML into a `WfsCapabilities` dataclass (feature types, CRS, output formats,
  bounding boxes, paging support).
- **`get_feature_gml(base_url, type_name, ...)`** — single-page `GetFeature`
  request returning raw GML 3.2 bytes.
- **`get_feature_geojson(base_url, type_name, ...)`** — single-page
  `GetFeature` request returning parsed GeoJSON. Suitable for simple feature
  types; complex INSPIRE types may produce truncated responses on some servers.
- **`iter_gml_pages(base_url, type_name, page_size, ...)`** — paginated
  iterator using `startIndex` / `count`. Yields one GML response (bytes) per
  page. Stops when a page returns fewer members than requested or the
  `max_features` cap is reached.
- **`fetch_all_gml(...)`** — convenience wrapper that collects all pages into a
  list.

### `gml_parser.py`

Parses WFS GML 3.2 responses into flat `list[dict]` records. Currently
supports:

- **`parse_timeseries_observations(gml_bytes)`** — handles INSPIRE
  `omso:PointTimeSeriesObservation` features. Flattens each weather station's
  embedded `wml2:MeasurementTimeseries` into one record per
  `(station, timestamp, value)` triple.

  Output schema:

  | Column | Type | Description |
  | --- | --- | --- |
  | `station_id` | string | GML identifier for the observation point |
  | `observed_property` | string | xlink:href to the observed property definition |
  | `latitude` | float | Station latitude (from `gml:pos`) |
  | `longitude` | float | Station longitude (from `gml:pos`) |
  | `period_begin` | string | Start of the phenomenon time period |
  | `period_end` | string | End of the phenomenon time period |
  | `timestamp` | string | Individual measurement timestamp |
  | `value` | float | Measured value (tenths of degrees Celsius for KNMI temperature) |

### `__main__.py`

CLI driver. Run from the `data-solution-2026/` directory:

```powershell
# Show service capabilities
python -m Extractors.wfs --mapping knmi-daggegevens-temperature --info

# Extract 4 stations, 2 per page, cap at 500 parsed records
python -m Extractors.wfs --mapping knmi-daggegevens-temperature --page-size 2 --max-features 4 --limit 500

# Extract with default page size from config
python -m Extractors.wfs --mapping knmi-daggegevens-temperature
```

## Configuration

The extractor is driven by a DWA-style JSON mapping stored at
`DataObjectMappings/knmi-daggegevens.json`. Key extensions on the mapping:

| Extension key | Purpose |
| --- | --- |
| `wfs_type_name` | WFS feature type to request (e.g. `omso:PointTimeSeriesObservation`) |
| `wfs_output_format` | Preferred output format (`application/gml+xml; version=3.2`) |
| `wfs_page_size` | Features per page for `startIndex` pagination |
| `gml_parser` | Parser function name (e.g. `timeseries_observations`) |
| `landing_path_template` | Parquet output path template with `{dataset}`, `{table}`, `{date}` placeholders |

## Pagination

WFS 2.0 defines `startIndex` (0-based) and `count` for server-side result
paging. The client sends both parameters on every request and advances
`startIndex` by the number of features returned. Pagination stops when:

- A page returns 0 features.
- A page returns fewer features than `count` (dataset exhausted).
- The `max_features` cap is reached.

Some WFS servers advertise `ImplementsResultPaging=FALSE` in their capabilities
but still honour `startIndex` — this has been confirmed for the KNMI service on
haleconnect.com.

## Adding a new feature type parser

1. Add a `parse_<name>(gml_bytes, *, max_rows=None) -> list[dict]` function to
   `gml_parser.py`.
2. Register it in the `_PARSERS` dict in `__main__.py`.
3. Create a mapping JSON in `DataObjectMappings/` with `gml_parser` set to
   `<name>`.

## Current data source

- **Service:** KNMI Gecontroleerde klimatologische daggegevens (controlled
  daily climate observations)
- **Provider:** KNMI (Koninklijk Nederlands Meteorologisch Instituut)
- **Endpoint:** `https://haleconnect.com/ows/services/org.874.cb9ca55e-f4e7-4bd8-a02e-75d528e22118_wfs/org.874.794fa9da-8bf0-4053-83d8-1174f2317dcb`
- **Feature type:** `omso:PointTimeSeriesObservation`
- **Coverage:** 33 automatic weather stations across the Netherlands, daily
  temperature observations since 1881
