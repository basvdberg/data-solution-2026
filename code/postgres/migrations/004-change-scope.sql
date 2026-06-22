-- Add change_scope to poller and extract_run_audit (event-based orchestration glossary).

alter table poller
    add column if not exists change_scope text;

alter table extract_run_audit
    add column if not exists change_scope text;

drop view if exists poller_latest_first;

create view poller_latest_first as
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
