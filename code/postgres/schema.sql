-- Runtime metadata for data-solution-2026 (BasNAS PoC).
-- Applied automatically by the poller on first connect; kept in Git as reference.

create table if not exists poller (
    id bigserial primary key,
    event_id text not null,
    run_id text not null,
    data_object_id text not null,
    source_data_object_id text not null,
    target_data_object_id text not null,
    event_type text not null,
    polled_at_utc timestamptz not null,
    old_marker text,
    new_marker text not null,
    inserted_at_utc timestamptz not null default now()
);

create index if not exists poller_data_object_polled_idx
    on poller (data_object_id, polled_at_utc desc, id desc);
