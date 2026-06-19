-- Recreate public.poller so event_id and run_id are last (matches code/postgres/schema.sql).
-- PostgreSQL cannot reorder columns in place; copy rows into a new table.

drop view if exists poller_latest_first;

alter table poller rename to poller_old;

create table poller (
    id bigserial primary key,
    polled_at_utc timestamptz not null,
    data_object_id text not null,
    event_type text not null,
    old_marker text,
    new_marker text not null,
    event_id text not null,
    run_id text not null
);

insert into poller (
    id,
    polled_at_utc,
    data_object_id,
    event_type,
    old_marker,
    new_marker,
    event_id,
    run_id
)
select
    id,
    polled_at_utc,
    data_object_id,
    event_type,
    old_marker,
    new_marker,
    event_id,
    run_id
from poller_old
order by id;

select setval(
    pg_get_serial_sequence('poller', 'id'),
    coalesce((select max(id) from poller), 1),
    true
);

drop table poller_old;

create index if not exists poller_data_object_polled_idx
    on poller (data_object_id, polled_at_utc desc, id desc);

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

grant select, insert on table public.poller to "data-solution-2026_app";
grant usage, select on sequence public.poller_id_seq to "data-solution-2026_app";
