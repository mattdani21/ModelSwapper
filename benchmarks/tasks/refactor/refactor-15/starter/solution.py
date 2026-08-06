"""Tiny command dispatcher."""


def process_command(command, args, ctx):
    if command == "add":
        if len(args) != 2:
            raise ValueError(f"{command} expects 2 arguments")
        key, value = args
        ctx[key] = value
        return f"added {key}"
    if command == "del":
        if len(args) != 1:
            raise ValueError(f"{command} expects 1 argument")
        key = args[0]
        if key not in ctx:
            raise KeyError(key)
        del ctx[key]
        return f"deleted {key}"
    if command == "set":
        if len(args) != 2:
            raise ValueError(f"{command} expects 2 arguments")
        key, value = args
        if key not in ctx:
            raise KeyError(key)
        ctx[key] = value
        return f"updated {key}"
    raise ValueError(f"unknown command {command}")
