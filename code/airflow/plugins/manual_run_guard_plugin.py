"""Fail manual DAG runs immediately when the same DAG is already running or queued."""

from __future__ import annotations

from airflow.listeners import hookimpl
from airflow.plugins_manager import AirflowPlugin

from dag_run_guard import fail_manual_dag_run_if_busy


class ManualRunGuardListener:
    @hookimpl
    def on_dag_run_queued(self, dag_run, *, session, msg) -> None:
        fail_manual_dag_run_if_busy(dag_run, session)

    @hookimpl
    def on_dag_run_running(self, dag_run, *, session, msg) -> None:
        fail_manual_dag_run_if_busy(dag_run, session)


class ManualRunGuardPlugin(AirflowPlugin):
    name = "manual_run_guard"
    listeners = [ManualRunGuardListener()]
