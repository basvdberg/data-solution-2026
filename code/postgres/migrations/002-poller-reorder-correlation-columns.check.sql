-- Applicable when public.poller exists and event_id is not after new_marker
-- (legacy tables kept event_id and run_id immediately after id).
select 1
where exists (
    select 1
    from information_schema.tables
    where table_schema = 'public'
      and table_name = 'poller'
)
and exists (
    select 1
    from information_schema.columns event_id_col
    join information_schema.columns new_marker_col
      on event_id_col.table_schema = new_marker_col.table_schema
     and event_id_col.table_name = new_marker_col.table_name
    where event_id_col.table_schema = 'public'
      and event_id_col.table_name = 'poller'
      and event_id_col.column_name = 'event_id'
      and new_marker_col.column_name = 'new_marker'
      and event_id_col.ordinal_position < new_marker_col.ordinal_position
);
