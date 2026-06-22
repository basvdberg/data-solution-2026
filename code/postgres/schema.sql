-- Runtime metadata for data-solution-2026 (BasNAS PoC).
-- Applied by infra/postgres/create-app-user.sh (bootstrap) and incremental migrations
-- in code/postgres/migrations/ via infra/postgres/run-applicable-migrations.sh (deploy).
-- Canonical reference: code/postgres/schema.sql (also embedded in
-- extractor_and_poller.common.postgres_schema for PYTHONPATH-only reads).

create table if not exists poller (
    id bigserial primary key,
    polled_at_utc timestamptz not null,
    data_object_id text not null,
    event_type text not null,
    change_scope text,
    old_marker text,
    new_marker text not null,
    event_id text not null,
    run_id text not null
);

create index if not exists poller_data_object_polled_idx
    on poller (data_object_id, polled_at_utc desc, id desc);

create index if not exists poller_polled_at_desc_idx
    on poller (polled_at_utc desc, id desc);

-- Browse latest probe events first (e.g. pgAdmin, ad hoc SQL).
create or replace view poller_latest_first as
select
    id,
    polled_at_utc,
    data_object_id,
    event_type,
    change_scope,
    old_marker,
    new_marker,
    event_id,
    run_id
from poller
order by polled_at_utc desc, id desc;

create schema if not exists staging;

create table if not exists extract_run_audit (
    run_id text primary key,
    event_id text not null unique,
    mapping_id text not null,
    data_object_id text,
    marker text not null,
    change_scope text,
    event_type text,
    status text not null,
    started_at_utc timestamptz not null,
    finished_at_utc timestamptz,
    output_table text,
    row_count bigint
);

create index if not exists extract_run_audit_mapping_started_idx
    on extract_run_audit (mapping_id, started_at_utc desc);
