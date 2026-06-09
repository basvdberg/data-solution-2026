-- Applicable when public.poller exists and still has legacy columns or lacks poller_latest_first.
select 1
where exists (
    select 1
    from information_schema.tables
    where table_schema = 'public'
      and table_name = 'poller'
)
and (
    exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'poller'
          and column_name in (
              'source_data_object_id',
              'target_data_object_id',
              'inserted_at_utc'
          )
    )
    or not exists (
        select 1
        from information_schema.views
        where table_schema = 'public'
          and table_name = 'poller_latest_first'
    )
);
