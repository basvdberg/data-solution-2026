-- Add orchestration event metadata to extract_run_audit (event-based orchestration glossary).

alter table extract_run_audit
    add column if not exists data_object_id text;

alter table extract_run_audit
    add column if not exists event_type text;
