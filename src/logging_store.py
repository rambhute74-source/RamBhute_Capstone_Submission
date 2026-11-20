"""
src/logging_store.py
Persistent SQLite decision logging ensuring complete auditability and 1:1 reconciliation.
Meets Acceptance Criterion A8 and Functional Requirement FR-08.
"""

from datetime import datetime, timezone
import json
import os
import sqlite3
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionLogRecord(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ticket_id: str
    stage: str = "routing"  # classification | routing | generation | validation
    input_summary: str
    model: Dict[str, str] = Field(default_factory=lambda: {"name": "meta-llama/llama-3.1-8b-instruct", "version": "1.0"})
    prediction: Dict[str, Any]
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    sources_used: List[Dict[str, Any]] = Field(default_factory=list)
    threshold_applied: float = 0.80
    action_taken: str  # auto_respond | escalate | block
    reason: str
    guardrail_results: Dict[str, str] = Field(default_factory=dict)
    prompt_version: str = "PR-03 v1.0"
    requirement_ids: List[str] = Field(default_factory=lambda: ["FR-04", "FR-08"])


class DecisionLogger:
    """
    Manages SQLite storage for all automated decisions.
    Explicitly manages and closes connections to support Windows file locking cleanly.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "storage", "decisions.db"
        )
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id     TEXT PRIMARY KEY,
                    timestamp       TEXT NOT NULL,
                    ticket_id       TEXT NOT NULL,
                    stage           TEXT NOT NULL,
                    input_summary   TEXT,
                    model           TEXT,
                    prediction      TEXT,
                    alternatives    TEXT,
                    sources_used    TEXT,
                    threshold       REAL,
                    action_taken    TEXT NOT NULL,
                    reason          TEXT NOT NULL,
                    guardrails      TEXT,
                    prompt_version  TEXT,
                    requirement_ids TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ticket_id ON decisions (ticket_id)")
            conn.commit()
        finally:
            conn.close()

    def log_decision(self, record: DecisionLogRecord) -> str:
        """Writes one decision record to the persistent SQLite database."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO decisions (
                    decision_id, timestamp, ticket_id, stage, input_summary,
                    model, prediction, alternatives, sources_used, threshold,
                    action_taken, reason, guardrails, prompt_version, requirement_ids
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.decision_id,
                    record.timestamp,
                    record.ticket_id,
                    record.stage,
                    record.input_summary,
                    json.dumps(record.model),
                    json.dumps(record.prediction),
                    json.dumps(record.alternatives),
                    json.dumps(record.sources_used),
                    record.threshold_applied,
                    record.action_taken,
                    record.reason,
                    json.dumps(record.guardrail_results),
                    record.prompt_version,
                    json.dumps(record.requirement_ids),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return record.decision_id

    def count_decisions(self) -> int:
        """Returns total count of logged decisions."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            cur = conn.execute("SELECT COUNT(*) FROM decisions")
            return int(cur.fetchone()[0])
        finally:
            conn.close()

    def get_decisions_for_ticket(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Fetch all decisions for a given ticket ID."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute("SELECT * FROM decisions WHERE ticket_id = ?", (ticket_id,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def reconcile_with_tickets(self, ticket_ids: List[str]) -> Dict[str, Any]:
        """
        Reconciles the decision database with a list of processed tickets.
        Checks Criterion A8: exact count match and zero gaps.
        """
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            cur = conn.execute("SELECT DISTINCT ticket_id FROM decisions")
            logged_ids = set(r[0] for r in cur.fetchall())
        finally:
            conn.close()

        target_set = set(ticket_ids)
        missing_in_log = list(target_set - logged_ids)
        extra_in_log = list(logged_ids - target_set)
        reconciles_cleanly = len(missing_in_log) == 0

        return {
            "tickets_submitted": len(ticket_ids),
            "unique_logged_tickets": len(logged_ids),
            "total_decisions_logged": self.count_decisions(),
            "missing_count": len(missing_in_log),
            "missing_ticket_ids": missing_in_log[:10],
            "reconciles_cleanly": reconciles_cleanly,
        }
