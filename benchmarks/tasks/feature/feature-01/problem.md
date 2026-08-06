# Task: is_palindrome

Implement `is_palindrome(text)` in `solution.py`.

Given a string, return `True` if it reads the same forwards and backwards when only its letters and digits are considered, ignoring case. All other characters (spaces, punctuation, symbols) are ignored.

Examples:

- `is_palindrome("A man, a plan, a canal: Panama")` -> `True`
- `is_palindrome("race a car")` -> `False`
- `is_palindrome("Was it a car or a cat I saw?")` -> `True`
- `is_palindrome("12321")` -> `True`
- `is_palindrome("")` -> `True`
- `is_palindrome("hello")` -> `False`

Edge cases:

- Empty string and whitespace-only strings count as palindromes (`True`).
- A single character is a palindrome.
- Digits are significant: `"12 21"` -> `True`, `"123"` -> `False`.
- Case is ignored: `"No 'x' in Nixon"` -> `True`.

Do not change the function signature. Do not add prints.
