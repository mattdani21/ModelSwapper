"""Context Capsule v0 — model-agnostic working state for the swap runtime.

ADR-0002: the capsule is the unit of context handoff between swapped
specialists. Serialized to JSON, append-only within a run, round-trip
byte-identical. This module owns load/save/validate; no other module
pokes at the JSON directly.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import uuid
from typing import Any, Optional

SCHEMA_VERSION = "0.1.0"
_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_v0.json")

try:
    import jsonschema  # optional; needed for strict schema validation
    _HAS_JSCONSCHEMA = True
except Exception:  # pragma: no cover
    _HAS_JSCONSCHEMA = False


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class CapsuleError(ValueError):
    """Raised on invalid capsule mutations or malformed JSON."""


class Capsule:
    """Context Capsule v0 wrapper over a plain dict (JSON-serializable)."""

    def __init__(self, data: dict[str, Any]):
        self.data = data

    # -- construction ----------------------------------------------------
    @classmethod
    def new(
        cls,
        task_id: str,
        goal: str,
        constraints: Optional[list[str]] = None,
        run_id: Optional[str] = None,
        budget: Optional[dict[str, int]] = None,
    ) -> "Capsule":
        now = _now()
        data = {
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "goal": goal,
            "constraints": list(constraints or []),
            "plan": [],
            "artifacts": [],
            "decisions_log": [],
            "phase_history": [],
            "meta": {
                "created_at": now,
                "updated_at": now,
                "capsule_version": SCHEMA_VERSION,
                "run_id": run_id or uuid.uuid4().hex[:12],
                "budget": {"max_loop_iterations": 5, "max_tokens": 16000, **(budget or {})},
            },
        }
        return cls(data)

    # -- serialization ---------------------------------------------------
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.data, indent=indent, ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, text: str) -> "Capsule":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise CapsuleError(f"capsule is not valid JSON: {e}") from e
        if not isinstance(data, dict):
            raise CapsuleError("capsule root must be a JSON object")
        return cls(data)

    def save(self, path: str) -> None:
        """Atomic write (temp file + rename)."""
        text = self.to_json()
        d = os.path.dirname(os.path.abspath(path))
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    @classmethod
    def load(cls, path: str) -> "Capsule":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    # -- validation ------------------------------------------------------
    def validate(self, strict: bool = True) -> list[str]:
        """Return list of problems (empty list = valid).

        strict=True additionally runs jsonschema when it is installed.
        """
        problems: list[str] = []
        d = self.data
        required = [
            "schema_version", "task_id", "goal", "constraints", "plan",
            "artifacts", "decisions_log", "phase_history", "meta",
        ]
        for k in required:
            if k not in d:
                problems.append(f"missing required key: {k}")
        if d.get("schema_version") != SCHEMA_VERSION:
            problems.append(f"schema_version must be {SCHEMA_VERSION!r}")
        for key in ("constraints", "plan", "artifacts", "decisions_log", "phase_history"):
            if key in d and not isinstance(d[key], list):
                problems.append(f"{key} must be a list")
        if strict and _HAS_JSCONSCHEMA:
            try:
                with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                jsonschema.validate(d, schema)
            except jsonschema.ValidationError as e:
                problems.append(f"jsonschema: {e.message}")
            except OSError as e:
                problems.append(f"cannot read schema file: {e}")
        return problems

    # -- append-only mutations -------------------------------------------
    def _touch(self) -> None:
        self.data["meta"]["updated_at"] = _now()

    def add_constraint(self, constraint: str) -> None:
        self.data["constraints"].append(constraint)
        self._touch()

    def set_plan(self, steps: list[dict[str, str]]) -> None:
        self.data["plan"] = steps
        self._touch()

    def add_artifact(self, path: str, content: str, kind: str = "code") -> None:
        if kind not in ("code", "diff", "test", "other"):
            raise CapsuleError(f"invalid artifact kind: {kind}")
        self.data["artifacts"].append({"path": path, "content": content, "kind": kind})
        self._touch()

    def add_decision(self, phase: str, decision: str, rationale: str) -> None:
        self.data["decisions_log"].append(
            {"at": _now(), "phase": phase, "decision": decision, "rationale": rationale}
        )
        self._touch()

    def complete_phase(
        self,
        phase: str,
        model: str,
        outcome: str = "ok",
        swap_in_ms: Optional[float] = None,
        swap_out_ms: Optional[float] = None,
        tokens: Optional[int] = None,
    ) -> None:
        if outcome not in ("ok", "retry", "fail"):
            raise CapsuleError(f"invalid outcome: {outcome!r}")
        now = _now()
        entry = {
            "phase": phase,
            "model": model,
            "started_at": now,
            "finished_at": now,
            "outcome": outcome,
            "swap_in_ms": swap_in_ms,
            "swap_out_ms": swap_out_ms,
            "tokens": tokens,
            "capsule_bytes": self.bytes(),
            "capsule_tokens_est": max(1, len(self.to_json()) // 4),
        }
        self.data["phase_history"].append(entry)
        self._touch()

    def bytes(self) -> int:
        return len(self.to_json().encode("utf-8"))
