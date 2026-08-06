import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import LRUCache


def test_get_missing_returns_minus_one():
    cache = LRUCache(2)
    assert cache.get(1) == -1


def test_put_and_get():
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == 10
    assert cache.get(2) == 20


def test_eviction_lru():
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.get(1)          # 1 becomes most recent
    cache.put(3, 30)      # evicts 2
    assert cache.get(2) == -1
    assert cache.get(1) == 10
    assert cache.get(3) == 30


def test_update_does_not_evict():
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.put(1, 99)
    cache.put(3, 30)      # evicts 2, not 1
    assert cache.get(1) == 99
    assert cache.get(2) == -1


def test_update_refreshes_recency():
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.put(1, 99)      # 1 now most recent
    cache.put(3, 30)      # evicts 2
    assert cache.get(2) == -1
    assert cache.get(1) == 99


def test_capacity_one():
    cache = LRUCache(1)
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == -1
    assert cache.get(2) == 20


def test_get_refreshes_recency():
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.get(1)
    cache.put(3, 30)
    assert cache.get(2) == -1
    assert cache.get(1) == 10


def test_invalid_capacity_raises():
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-3)


def test_evicted_key_stays_evicted():
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.put(3, 30)
    assert cache.get(1) == -1
    cache.put(1, 10)
    assert cache.get(1) == 10
    assert cache.get(2) == -1
