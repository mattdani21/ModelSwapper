def sum_even_numbers(nums):
    """Return the sum of all even integers in nums."""
    total = 0
    for n in nums:
        if n % 2 == 0:
            total += n
    return total
