def run_length_encode(s):
    """Run-length encode s as char + run length for every run."""
    if not s:
        return ""
    parts = []
    count = 1
    for i in range(len(s) - 1):
        if s[i] == s[i + 1]:
            count += 1
        else:
            parts.append(s[i] + str(count))
            count = 0
    parts.append(s[-1] + str(count))
    return "".join(parts)
