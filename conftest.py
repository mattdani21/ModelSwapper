"""Repo-root conftest: guarantees the repo root is FIRST on sys.path.

Pytest's import-mode handling of multiple directory args can resolve
namespace collisions differently per invocation (observed: `capsule`
shadowed when collecting capsule/tests together with other test dirs).
This makes test collection deterministic regardless of invocation.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT in sys.path:
    sys.path.remove(_ROOT)
sys.path.insert(0, _ROOT)
