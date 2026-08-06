"""Small reporting helpers."""


def format_row(name, value):
    return f"{name:<12} {value:>6}"


def print_inventory(items):
    print("INVENTORY")
    print("=" * 20)
    for name, qty in items:
        print(format_row(name, qty))
    print()


def print_scores(scores):
    print("SCORES")
    print("=" * 20)
    for name, pts in scores:
        print(format_row(name, pts))
    print()
