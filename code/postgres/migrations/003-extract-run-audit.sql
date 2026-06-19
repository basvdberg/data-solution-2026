-- Extract idempotency audit table (see code/postgres/schema.sql).
create schema if not exists staging;

create table if not exists extract_run_audit (
    run_id text primary key,
    event_id text not null unique,
    mapping_id text not null,
    marker text not null,
    status text not null,
    started_at_utc timestamptz not null,
    finished_at_utc timestamptz,
    output_table text,
    row_count bigint
);

create index if not exists extract_run_audit_mapping_started_idx
    on extract_run_audit (mapping_id, started_at_utc desc);
