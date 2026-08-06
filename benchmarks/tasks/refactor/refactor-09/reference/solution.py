"""Banking request handler."""

TOKENS = {"alice": "tok-1", "bob": "tok-2"}
BALANCES = {"alice": 100.0, "bob": 50.0}


def _parse(raw):
    parts = raw.split("|")
    if len(parts) != 3:
        raise ValueError("malformed request")
    token, account, amount_s = [p.strip() for p in parts]
    try:
        amount = float(amount_s)
    except ValueError:
        raise ValueError("bad amount") from None
    if amount <= 0:
        raise ValueError("bad amount")
    return token, account, amount


def _authorize(account, token):
    if TOKENS.get(account) != token:
        raise PermissionError("bad token")


def _apply(account, amount):
    if account not in BALANCES:
        raise KeyError(account)
    balance = BALANCES[account]
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount


def _format(account, new_balance):
    return f"{account}:{new_balance:.2f}"


def handle_request(raw):
    token, account, amount = _parse(raw)
    _authorize(account, token)
    new_balance = _apply(account, amount)
    return _format(account, new_balance)
