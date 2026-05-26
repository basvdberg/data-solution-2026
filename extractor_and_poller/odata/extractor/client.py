"""Generic OData v4 client.

No source-specific logic lives here. The two entry points are:

- :func:`fetch_singleton` — GET a single entity such as ``.../Properties``.
- :func:`fetch_all` — GET all rows of a collection endpoint, paginated.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Iterator
from urllib.parse import urljoin

import requests

log = logging.getLogger(__name__)

_DEFAULT_HEADERS = {"Accept": "application/json"}


def _session(session: requests.Session | None) -> tuple[requests.Session, bool]:
    if session is not None:
        return session, False
    return requests.Session(), True


def _parse_json(response: requests.Response) -> dict[str, Any]:
    """BOM-tolerant JSON decode (services.odata.org returns UTF-8 BOM)."""
    return json.loads(response.content.decode("utf-8-sig"))


def fetch_singleton(
    url: str,
    *,
    session: requests.Session | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Fetch a single OData entity.

    Returns the parsed JSON body. If the server wraps the entity in
    ``{"value": [...]}``, the first element is returned; otherwise the body
    is returned as-is.
    """
    s, owned = _session(session)
    try:
        r = s.get(url, headers=_DEFAULT_HEADERS, timeout=timeout)
        r.raise_for_status()
        body = _parse_json(r)
        value = body.get("value")
        if isinstance(value, list) and value:
            return value[0]
        return body
    finally:
        if owned:
            s.close()


def iter_pages(
    url: str,
    *,
    page_size: int | None = None,
    session: requests.Session | None = None,
    timeout: float = 120.0,
) -> Iterator[list[dict[str, Any]]]:
    """Yield successive page payloads (``body["value"]`` lists) for a collection.

    ``$top`` is added to the *first* request only when ``page_size`` is given;
    subsequent pages follow ``@odata.nextLink`` verbatim so any ``$skip`` that
    the server picks is preserved.
    """
    s, owned = _session(session)
    try:
        current_url: str | None = url
        first = True
        page_no = 0
        while current_url:
            if first and page_size:
                sep = "&" if "?" in current_url else "?"
                current_url = f"{current_url}{sep}$top={int(page_size)}"
            page_no += 1
            log.debug("GET (page %d) %s", page_no, current_url)
            r = s.get(current_url, headers=_DEFAULT_HEADERS, timeout=timeout)
            r.raise_for_status()
            body = _parse_json(r)
            rows = body.get("value", []) or []
            log.debug("  -> %d rows", len(rows))
            yield rows
            raw_next = body.get("@odata.nextLink")
            if not raw_next:
                current_url = None
            elif "://" in raw_next:
                current_url = raw_next
            else:
                current_url = urljoin(current_url, raw_next)
            first = False
    finally:
        if owned:
            s.close()


def fetch_all(
    url: str,
    *,
    page_size: int | None = None,
    max_rows: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch every row of a collection endpoint, following ``@odata.nextLink``.

    ``page_size`` is a *hint* sent as ``$top`` on the first request only.
    OData v4 servers are free to interpret ``$top`` two ways:

    1. *Per-page hint* (e.g. CBS): caps the size of each page, but the server
       still returns ``@odata.nextLink`` until the dataset is exhausted.
    2. *Total result cap* (e.g. the public Northwind reference service): caps
       the overall result count regardless of pagination.

    When in doubt, pass ``page_size=None`` (the default) so the server picks
    its own page size and we just follow ``@odata.nextLink`` to exhaustion.
    ``max_rows`` is a client-side cap that always applies.
    """
    out: list[dict[str, Any]] = []
    with requests.Session() as s:
        for rows in iter_pages(url, page_size=page_size, session=s):
            out.extend(rows)
            if max_rows is not None and len(out) >= max_rows:
                return out[:max_rows]
    return out
