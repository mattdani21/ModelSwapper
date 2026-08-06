# Task: fizzbuzz

Implement `fizzbuzz(n)` in `solution.py`.

Given a positive integer `n`, return a list of strings for the numbers `1` through `n` inclusive:

- `"FizzBuzz"` when the number is divisible by both 3 and 5
- `"Fizz"` when divisible by 3 (but not 5)
- `"Buzz"` when divisible by 5 (but not 3)
- otherwise the number itself as a string

Raise `ValueError` if `n` is less than 1.

Examples:

- `fizzbuzz(1)` -> `["1"]`
- `fizzbuzz(3)` -> `["1", "2", "Fizz"]`
- `fizzbuzz(5)` -> `["1", "2", "Fizz", "4", "Buzz"]`
- `fizzbuzz(15)[14]` -> `"FizzBuzz"`
- `fizzbuzz(15)[2]` -> `"Fizz"`
- `fizzbuzz(15)[4]` -> `"Buzz"`
- `fizzbuzz(0)` raises `ValueError`
- `fizzbuzz(-3)` raises `ValueError`

Edge cases:

- `n == 1` returns a single-element list.
- Multiples of 15 must yield `"FizzBuzz"`, not `"Fizz"` or `"Buzz"`.

Do not change the function signature. Do not add prints.
