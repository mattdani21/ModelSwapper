def evaluate_rpn(tokens):
    """Evaluate a Reverse Polish Notation expression.

    Operands may be integers or decimal numeric strings. Integer division
    truncates toward zero. Raises ValueError on any malformed expression
    or division by zero.
    """
    ops = {"+", "-", "*", "/"}
    stack = []
    for tok in tokens:
        if tok in ops:
            if len(stack) < 2:
                raise ValueError("not enough operands")
            b = stack.pop()
            a = stack.pop()
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:
                if b == 0:
                    raise ValueError("division by zero")
                q = abs(a) // abs(b)
                if (a < 0) != (b < 0):
                    q = -q
                stack.append(q)
        elif isinstance(tok, bool):
            raise ValueError(f"invalid token: {tok!r}")
        elif isinstance(tok, int):
            stack.append(tok)
        elif isinstance(tok, str):
            try:
                stack.append(int(tok))
            except ValueError:
                raise ValueError(f"invalid token: {tok!r}")
        else:
            raise ValueError(f"invalid token: {tok!r}")
    if len(stack) != 1:
        raise ValueError("invalid expression")
    return stack[0]
