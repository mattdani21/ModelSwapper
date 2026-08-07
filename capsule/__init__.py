"""Context Capsule package (ADR-0002)."""
from .capsule import SCHEMA_VERSION, Capsule, CapsuleError

__all__ = ["Capsule", "CapsuleError", "SCHEMA_VERSION"]
