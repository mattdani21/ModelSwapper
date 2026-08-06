def valid_parentheses(s):
    """Return True if s is a correctly matched bracket sequence."""
    stack = []
    for c in s:
        if c in "([{":
            stack.append(c)
        else:
            if not stack:
                return False
            stack.pop()
    return not stack
