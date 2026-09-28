"""Mock OCI tools with fixed synthetic data. Read-only by design."""

from __future__ import annotations

INSTANCES = [
    {"id": "i-0a1b2c", "name": "dev-box", "state": "RUNNING", "shape": "VM.Standard.E2.1"},
    {"id": "i-9z8y7x", "name": "prod-api", "state": "RUNNING", "shape": "VM.Standard.E2.4"},
]

METRICS = {
    "i-0a1b2c": {"cpu_avg_pct_7d": 2.1, "idle_cost_usd_month": 18.40},
    "i-9z8y7x": {"cpu_avg_pct_7d": 61.4, "idle_cost_usd_month": 0.0},
}

LOGS = [
    {"ts": "2026-09-20T03:12:00Z", "level": "INFO", "msg": "backup completed"},
    {"ts": "2026-09-20T03:14:10Z", "level": "ERROR", "msg": "volume attachment timeout for ocid1.volume.oc1..aaaa1111"},
    {"ts": "2026-09-20T03:14:11Z", "level": "ERROR", "msg": "retry failed for ocid1.volume.oc1..aaaa1111"},
    {"ts": "2026-09-20T03:15:02Z", "level": "ERROR", "msg": "operator notified at oncall@example.com"},
]

BUDGET = {"limit_usd": 500.0, "spent_usd": 412.30, "forecast_exhaust_day": 26}


class ToolError(Exception):
    pass


def list_instances() -> list[dict]:
    return INSTANCES


def get_metrics(instance_id: str) -> dict:
    if instance_id not in METRICS:
        raise ToolError(f"unknown instance id: {instance_id}")
    return {"instance_id": instance_id, **METRICS[instance_id]}


def search_logs(term: str) -> list[dict]:
    term_l = term.lower()
    return [row for row in LOGS if term_l in row["level"].lower() or term_l in row["msg"].lower()]


def get_budget() -> dict:
    return BUDGET


TOOLS = {
    "list_instances": list_instances,
    "get_metrics": get_metrics,
    "search_logs": search_logs,
    "get_budget": get_budget,
}
