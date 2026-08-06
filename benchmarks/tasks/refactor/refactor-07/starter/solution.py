"""Table and CSV rendering."""


def print_table(rows):
    for row in rows:
        cells = [str(c) for c in row]
        print("|" + "|".join(f" {c} " for c in cells) + "|")


def print_csv(rows):
    for row in rows:
        cells = [str(c) for c in row]
        print(",".join(cells))
