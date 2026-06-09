-- Grants for the data-solution-2026 application role on database "data-solution-2026".
-- Run via infra/postgres/create-app-user.sh (idempotent).

grant connect on database "data-solution-2026" to "data-solution-2026_app";

grant usage, create on schema public to "data-solution-2026_app";

grant select, insert on table public.poller to "data-solution-2026_app";
grant usage, select on sequence public.poller_id_seq to "data-solution-2026_app";

grant select, insert, update on table public.extract_run_audit to "data-solution-2026_app";

grant usage, create on schema staging to "data-solution-2026_app";
grant select, insert, update, delete, truncate on all tables in schema staging
    to "data-solution-2026_app";

alter default privileges in schema public
    grant select, insert on tables to "data-solution-2026_app";
alter default privileges in schema public
    grant usage, select on sequences to "data-solution-2026_app";
alter default privileges in schema staging
    grant select, insert, update, delete, truncate on tables to "data-solution-2026_app";
