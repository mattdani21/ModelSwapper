def fizzbuzz(n):
    """Return the FizzBuzz sequence for 1..n as a list of strings.

    Raises ValueError if n < 1.
    """
    if n < 1:
        raise ValueError("n must be a positive integer")
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
