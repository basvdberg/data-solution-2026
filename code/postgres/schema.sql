-- Runtime metadata for data-solution-2026 (BasNAS PoC).
-- Applied by infra/postgres/create-app-user.sh and by the poller on first connect.
-- Canonical copy for the application: code/postgres/schema.sql (also embedded in
-- extractor_and_poller.common.postgres_schema for PYTHONPATH-only runs).

create table if not exists poller (
    id bigserial primary key,
    polled_at_utc timestamptz not null,
    data_object_id text not null,
    event_type text not null,
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
    old_marker,
    new_marker,
    event_id,
    run_id
from poller
order by polled_at_utc desc, id desc;
