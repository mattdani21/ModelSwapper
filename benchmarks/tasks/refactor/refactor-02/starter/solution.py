"""Small reporting helpers."""


def print_inventory(items):
    print("INVENTORY")
    print("=" * 20)
    for name, qty in items:
        print(f"{name:<12} {qty:>6}")
    print()


def print_scores(scores):
    print("SCORES")
    print("=" * 20)
    for name, pts in scores:
        print(f"{name:<12} {pts:>6}")
    print()
