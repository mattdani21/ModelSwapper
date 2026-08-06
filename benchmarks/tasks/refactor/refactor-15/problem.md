# Task: extract a command dispatcher

`solution.py` has one public function `process_command(command, args, ctx)`
that handles three commands (`add`, `del`, `set`) inline. The argument-arity
check is duplicated across the command branches, as is the missing-key check.

Refactor the module so that:

- Add a helper `_validate_args(command, args, expected)` that raises
  `ValueError` with message `"{command} expects {expected} arguments"` when
  `len(args) != expected`. The arity check must appear exactly once, inside
  this helper.
- Add a helper `_require_key(ctx, key)` that raises `KeyError(key)` when the
  key is absent. The check must appear exactly once, inside this helper.
- Add one handler per command: `_handle_add(args, ctx)`, `_handle_del(args,
  ctx)`, `_handle_set(args, ctx)` with the current per-command behavior
  (including the returned strings `"added <key>"`, `"deleted <key>"`,
  `"updated <key>"`).
- Dispatch through a module-level dict `_HANDLERS` mapping command names to
  handlers, plus a module-level dict `_ARITY` mapping each command to its
  expected argument count (add: 2, del: 1, set: 2). Unknown commands keep
  raising `ValueError` with message `"unknown command <command>"`.
- `process_command(command, args, ctx)` keeps its signature and behavior and
  must contain none of the per-command logic itself — only the unknown-
  command check, arity validation, and the handler call.

Do not change behavior or error messages. Stdlib only.
