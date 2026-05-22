"""KNMI Data Platform (KDP) Open Data API — list files and probe for changes.

API guide: https://developer.dataplatform.knmi.nl/open-data-api

Change detection lists the newest file in a dataset (``maxKeys=1``, ``orderBy``,
``sorting``) and uses ``filename`` or a timestamp field as the baseline marker.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.dataplatform.knmi.nl/open-data/v1"


def _resolve_api_key(
    *,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
) -> str:
    key = api_key or os.environ.get(api_key_env, "")
    if not key:
        raise KeyError(
            f"KNMI Open Data API requires an API key in ${api_key_env} "
            "(register at https://developer.dataplatform.knmi.nl/open-data-api)"
        )
    return key


def list_files(
    dataset_name: str,
    dataset_version: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
    max_keys: int = 1,
    order_by: str = "created",
    sorting: str = "desc",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """GET ``.../datasets/{name}/versions/{version}/files``."""
    token = _resolve_api_key(api_key=api_key, api_key_env=api_key_env)
    url = f"{base_url.rstrip('/')}/datasets/{dataset_name}/versions/{dataset_version}/files"
    params = {
        "maxKeys": max_keys,
        "orderBy": order_by,
        "sorting": sorting,
    }
    log.info(
        "KDP list_files %s/%s (maxKeys=%s, orderBy=%s, sorting=%s)",
        dataset_name,
        dataset_version,
        max_keys,
        order_by,
        sorting,
    )
    r = requests.get(
        url,
        headers={"Authorization": token},
        params=params,
        timeout=timeout,
    )
    r.raise_for_status()
    body = r.json()
    if "error" in body:
        raise RuntimeError(f"KDP list_files error: {body['error']}")
    return body


def get_latest_file(
    dataset_name: str,
    dataset_version: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
    order_by: str = "created",
    sorting: str = "desc",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return the metadata dict for the newest file in a dataset version."""
    body = list_files(
        dataset_name,
        dataset_version,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
        max_keys=1,
        order_by=order_by,
        sorting=sorting,
        timeout=timeout,
    )
    files = body.get("files") or []
    if not files:
        raise ValueError(
            f"No files returned for {dataset_name}/{dataset_version} "
            f"(orderBy={order_by}, sorting={sorting})"
        )
    latest = files[0]
    log.info("KDP latest file: %s", latest.get("filename"))
    return latest


def probe_change_marker(
    dataset_name: str,
    dataset_version: str,
    *,
    marker_field: str = "filename",
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
    order_by: str = "created",
    sorting: str = "desc",
    timeout: float = 30.0,
) -> str:
    """Lightweight change probe: one list call, one marker string."""
    latest = get_latest_file(
        dataset_name,
        dataset_version,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
        order_by=order_by,
        sorting=sorting,
        timeout=timeout,
    )
    if marker_field not in latest:
        raise KeyError(
            f"Marker field '{marker_field}' not in latest file metadata. "
            f"Available: {sorted(latest.keys())}"
        )
    marker = str(latest[marker_field])
    log.info("KDP change marker (%s): %s", marker_field, marker)
    return marker


def get_file_url(
    dataset_name: str,
    dataset_version: str,
    filename: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """GET temporary download URL for one file in a dataset."""
    token = _resolve_api_key(api_key=api_key, api_key_env=api_key_env)
    url = (
        f"{base_url.rstrip('/')}/datasets/{dataset_name}/versions/{dataset_version}"
        f"/files/{filename}/url"
    )
    log.info("KDP get_file_url %s", filename)
    r = requests.get(url, headers={"Authorization": token}, timeout=timeout)
    r.raise_for_status()
    body = r.json()
    if "error" in body:
        raise RuntimeError(f"KDP get_file_url error: {body['error']}")
    return body


def download_file(
    dataset_name: str,
    dataset_version: str,
    filename: str,
    dest_path: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
    timeout: float = 600.0,
) -> str:
    """Resolve a temporary URL and stream the file to ``dest_path``."""
    meta = get_file_url(
        dataset_name,
        dataset_version,
        filename,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
    )
    download_url = meta.get("temporaryDownloadUrl")
    if not download_url:
        raise KeyError(f"No temporaryDownloadUrl in response for {filename}")

    log.info("Downloading %s -> %s", filename, dest_path)
    with requests.get(download_url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    log.info("Downloaded %d bytes", os.path.getsize(dest_path))
    return dest_path


def download_latest(
    dataset_name: str,
    dataset_version: str,
    dest_path: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    api_key_env: str = "KNMI_API_KEY",
    order_by: str = "created",
    sorting: str = "desc",
    timeout: float = 600.0,
) -> tuple[str, str]:
    """Download the newest catalog file. Returns ``(filename, dest_path)``."""
    latest = get_latest_file(
        dataset_name,
        dataset_version,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
        order_by=order_by,
        sorting=sorting,
        timeout=30.0,
    )
    filename = str(latest["filename"])
    download_file(
        dataset_name,
        dataset_version,
        filename,
        dest_path,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
        timeout=timeout,
    )
    return filename, dest_path
