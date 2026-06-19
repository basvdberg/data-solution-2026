-- Applicable when public.poller exists but extract_run_audit is missing.
select 1
where exists (
    select 1
    from information_schema.tables
    where table_schema = 'public'
      and table_name = 'poller'
)
and not exists (
    select 1
    from information_schema.tables
    where table_schema = 'public'
      and table_name = 'extract_run_audit'
);
