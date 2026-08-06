"""Tiny command dispatcher."""


def _validate_args(command, args, expected):
    if len(args) != expected:
        raise ValueError(f"{command} expects {expected} arguments")


def _require_key(ctx, key):
    if key not in ctx:
        raise KeyError(key)


def _handle_add(args, ctx):
    key, value = args
    ctx[key] = value
    return f"added {key}"


def _handle_del(args, ctx):
    key = args[0]
    _require_key(ctx, key)
    del ctx[key]
    return f"deleted {key}"


def _handle_set(args, ctx):
    key, value = args
    _require_key(ctx, key)
    ctx[key] = value
    return f"updated {key}"


_HANDLERS = {"add": _handle_add, "del": _handle_del, "set": _handle_set}
_ARITY = {"add": 2, "del": 1, "set": 2}


def process_command(command, args, ctx):
    if command not in _HANDLERS:
        raise ValueError(f"unknown command {command}")
    _validate_args(command, args, _ARITY[command])
    return _HANDLERS[command](args, ctx)
