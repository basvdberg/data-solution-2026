"""OGC WFS 2.0 extractor.

Modules:
    client      Generic WFS 2.0 HTTP client (GetCapabilities, GetFeature).
    gml_parser  Parse WFS GML 3.2 responses into flat dicts for Parquet.
"""

from extractor.wfs.client import (  # noqa: F401
    get_capabilities,
    get_feature_gml,
    get_feature_geojson,
    fetch_all_gml,
    iter_gml_pages,
    probe_change_marker,
)
from extractor.wfs.gml_parser import (  # noqa: F401
    extract_max_period_end,
    parse_timeseries_observations,
)
