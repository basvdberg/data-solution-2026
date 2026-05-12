"""OGC WFS 2.0 extractor.

Modules:
    client      Generic WFS 2.0 HTTP client (GetCapabilities, GetFeature).
    gml_parser  Parse WFS GML 3.2 responses into flat dicts for Parquet.
"""

from Extractors.wfs.client import (  # noqa: F401
    get_capabilities,
    get_feature_gml,
    get_feature_geojson,
    fetch_all_gml,
    iter_gml_pages,
)
from Extractors.wfs.gml_parser import parse_timeseries_observations  # noqa: F401
