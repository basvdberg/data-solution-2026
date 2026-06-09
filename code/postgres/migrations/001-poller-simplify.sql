-- Simplify public.poller columns; add latest-first view and polled_at index.
alter table poller drop column if exists source_data_object_id;
alter table poller drop column if exists target_data_object_id;
alter table poller drop column if exists inserted_at_utc;

create index if not exists poller_polled_at_desc_idx
    on poller (polled_at_utc desc, id desc);

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
