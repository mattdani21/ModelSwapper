def is_balanced(s):
    """Return True if (), [], and {} are balanced and properly nested.

    Non-bracket characters are ignored.
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
