def my_atoi(s):
    """Parse s as a 32-bit signed integer per the atoi rules."""
    s = s.lstrip()
    if not s:
        return 0
    sign = 1
    i = 0
    if s[0] in "+-":
        if s[0] == "-":
            sign = -1
        i = 1
    total = 0
    while i < len(s) and s[i].isdigit():
        total = total * 10 + int(s[i])
        i += 1
    result = sign * total
    if result > 2147483647:
        return 2147483647
    if result < -2147483648:
        return -2147483648
    return result
