# Task: extract a Logger class and remove module-level state

`solution.py` is an event logger built on module-level state: a global
`_level`, a global `_entries` list, and a global `_sequence` counter, mutated
by free functions `set_level`, `log`, `summary`, `recent`, `drain`. The level
validation is duplicated across `set_level` and `log`, and the severity
filter is a chain of special cases.

Refactor the module so that:

- Add a class `Logger` whose instances hold all state: the current level, the
  entries list, and the sequence counter. The constructor takes the initial
  level with default `"INFO"`. `Logger` provides methods `set_level(level)`,
  `log(level, msg)`, `summary()`, `recent(n)`, and `drain()`.
- Add a single module-level mapping `_SEVERITY` from level name to severity
  order (DEBUG < INFO < WARN < ERROR). The level-name validation must appear
  exactly once in the file, inside a private `Logger` method `_check_level`
  used by both level setting and `log`.
- Filtering rule (unchanged behavior): a message is recorded only when its
  severity is at least the logger's current severity.
- Entries are dicts `{"seq": <1-based running number>, "level": ...,
  "message": ...}`; the sequence keeps increasing across `drain()` calls.
  `recent(n)` returns the last `n` entries formatted as
  `"[{seq:03d}] {level}: {message}"`; `summary()` returns per-level counts;
  `drain()` returns all entries and clears them.
- Keep the module-level functions `set_level`, `log`, `summary`, `recent`,
  `drain` with their exact signatures as thin wrappers delegating to a single
  module-level default instance named `_store`.
- The raw module-level `_level`, `_entries`, and `_sequence` globals must be
  removed.

Do not change behavior. Stdlib only.
