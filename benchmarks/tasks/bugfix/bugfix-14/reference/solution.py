def valid_parentheses(s):
    """Return True if s is a correctly matched bracket sequence."""
    matching = {")": "(", "]": "[", "}": "{"}
    stack = []
    for c in s:
        if c in "([{":
            stack.append(c)
        else:
            if not stack or stack.pop() != matching[c]:
                return False
    return not stack
