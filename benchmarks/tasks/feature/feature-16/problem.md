# Task: LRUCache

Implement an LRU (least-recently-used) cache class in `solution.py`:

```python
class LRUCache:
    def __init__(self, capacity):
        ...
    def get(self, key):
        ...
    def put(self, key, value):
        ...
```

Behavior:

- `get(key)` returns the value stored for `key`, or `-1` if `key` is not present. A successful `get` makes the key the most recently used.
- `put(key, value)` inserts or updates `key` with `value`. Updating an existing key does not change the number of entries. After an insert, if the cache holds more than `capacity` entries, the least recently used key is evicted.
- `__init__` raises `ValueError` if `capacity < 1`.

Example:

```python
cache = LRUCache(2)
cache.put(1, 10)          # cache: {1: 10}
cache.put(2, 20)          # cache: {1: 10, 2: 20}
cache.get(1)              # -> 10, key 1 now most recent
cache.put(3, 30)          # evicts key 2; cache: {1: 10, 3: 30}
cache.get(2)              # -> -1
cache.get(3)              # -> 30
cache.put(1, 99)          # update key 1; cache: {1: 99, 3: 30}
cache.get(1)              # -> 99
```

Edge cases:

- Getting a missing key returns `-1` and does not insert anything.
- Updating an existing key refreshes its recency.
- With capacity 1, every new insert evicts the previous key.
- `LRUCache(0)` raises `ValueError`.

Do not change the class or method names. Do not add prints.
