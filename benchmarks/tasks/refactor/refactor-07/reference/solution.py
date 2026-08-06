"""Table and CSV rendering."""


def _render_row(cells, sep, wrap=None):
    parts = [str(c) for c in cells]
    if wrap is not None:
        parts = [f"{wrap}{c}{wrap}" for c in parts]
    return sep.join(parts)


def print_table(rows):
    for row in rows:
        print("|" + _render_row(row, "|", wrap=" ") + "|")


def print_csv(rows):
    for row in rows:
        print(_render_row(row, ","))
