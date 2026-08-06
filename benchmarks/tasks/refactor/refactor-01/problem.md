# Task: extract duplicated credential validation

`solution.py` is a small user-management module with two public functions,
`register_user(name, email)` and `login_user(name, email)`. Both functions
currently contain the same username/email validation block, copied verbatim
into each function.

Refactor the module so that:

- Add a module-level helper `validate_credentials(name, email)` that performs
  the full validation currently duplicated in the two functions:
  - strips the username and checks it is non-empty, at least 3 characters
    long, and alphanumeric after removing internal spaces;
  - strips and lowercases the email, and checks it contains exactly one `@`
    with a non-empty domain after it;
  - raises `ValueError("invalid username")` / `ValueError("invalid email")`
    on failure;
  - returns the cleaned `(name, email)` pair.
- `register_user(name, email)` and `login_user(name, email)` keep their exact
  signatures and their current behavior (the returned dicts are unchanged:
  `{"action": "register" | "login", "username": <cleaned name>, "email":
  <cleaned email>}`). Each must delegate validation to
  `validate_credentials` — the validation logic must appear exactly once in
  the file, inside the helper, and must not appear inside `register_user` or
  `login_user`.

Do not change public behavior, do not add prints. Stdlib only.
