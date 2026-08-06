# Task: split the request-handler monolith

`solution.py` has a single public function `handle_request(raw)` that mixes
four responsibilities inline: parsing the raw request, authorizing the caller,
applying the business rule, and formatting the result.

Refactor the module so that:

- `_parse(raw)`: splits on `"|"`, requires exactly 3 fields (else
  `ValueError("malformed request")`), strips each field, parses the amount as
  a float (a non-numeric amount raises `ValueError("bad amount")`), rejects
  non-positive amounts with the same message, and returns
  `(token, account, amount)`.
- `_authorize(account, token)`: raises `PermissionError("bad token")` when the
  token does not match the account's token in the `TOKENS` table.
- `_apply(account, amount)`: looks up the account's balance in `BALANCES`
  (an unknown account raises `KeyError`), raises
  `ValueError("insufficient funds")` when the amount exceeds the balance, and
  returns the new balance.
- `_format(account, new_balance)`: returns `"{account}:{new_balance:.2f}"`.
- `handle_request(raw)` keeps its signature and behavior and must contain none
  of the parsing/auth/business/formatting logic itself — only calls to the
  four helpers.

Do not change behavior or error messages. Stdlib only.
