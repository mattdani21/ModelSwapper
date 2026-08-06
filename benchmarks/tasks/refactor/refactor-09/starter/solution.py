"""Banking request handler."""

TOKENS = {"alice": "tok-1", "bob": "tok-2"}
BALANCES = {"alice": 100.0, "bob": 50.0}


def handle_request(raw):
    parts = raw.split("|")
    if len(parts) != 3:
        raise ValueError("malformed request")
    token = parts[0].strip()
    account = parts[1].strip()
    amount_s = parts[2].strip()
    if TOKENS.get(account) != token:
        raise PermissionError("bad token")
    try:
        amount = float(amount_s)
    except ValueError:
        raise ValueError("bad amount") from None
    if amount <= 0:
        raise ValueError("bad amount")
    if account not in BALANCES:
        raise KeyError(account)
    balance = BALANCES[account]
    if amount > balance:
        raise ValueError("insufficient funds")
    return f"{account}:{balance - amount:.2f}"
