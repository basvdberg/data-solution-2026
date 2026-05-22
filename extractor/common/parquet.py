"""Generic Parquet writer.

Takes a list of dict records, a path template, and template variables. The
template is a regular Python format string, e.g.::

    "./Data/000_Source/{dataset}/{table}/{date}.parquet"
"""

from __future__ import annotations

import logging
import os
from typing import Any, Mapping, Sequence

import pyarrow as pa
import pyarrow.parquet as pq

log = logging.getLogger(__name__)


def _render(template: str, variables: Mapping[str, str]) -> str:
    try:
        return template.format(**variables)
    except KeyError as exc:
        raise KeyError(
            f"template variable {exc.args[0]!r} required by '{template}' was not provided"
        ) from exc


def write(
    records: Sequence[Mapping[str, Any]],
    template: str,
    variables: Mapping[str, str],
    *,
    compression: str = "snappy",
) -> str:
    """Write ``records`` as a Parquet file at the rendered template path.

    Returns the absolute path of the file that was written. Parent directories
    are created on the fly. An empty input still produces a file (so downstream
    consumers can distinguish "ran, nothing changed" from "did not run").
    """
    path = _render(template, variables)
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    if records:
        table = pa.Table.from_pylist(list(records))
    else:
        log.warning("No records for '%s'; writing empty Parquet.", abs_path)
        table = pa.table({})

    pq.write_table(table, abs_path, compression=compression)
    log.info("Wrote %d rows -> %s", table.num_rows, abs_path)
    return abs_path
