select 1
where not exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'extract_run_audit'
      and column_name = 'event_type'
);
