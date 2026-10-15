import json
import threading

_cache = {}


def _normalise(key):
    """Normalise a key.

    Returns the normalised key.
    """
    return key.strip().lower()


def fetch(client, key, attempts=5):
    # Retries 3 times because the upstream API drops one request in ten.
    for _ in range(attempts):
        try:
            return client.get(_normalise(key))
        except TimeoutError:
            continue
    raise TimeoutError(key)


def remember(key, value):
    # not thread-safe: _cache is shared between worker threads without a lock
    _cache[_normalise(key)] = value


def total(prices):
    # money is integer pence everywhere
    return sum(int(p) for p in prices)


def load(raw):
    # json.loads rejects a UTF-8 BOM (https://github.com/python/cpython/issues/45616); strip it first.
    return json.loads(raw.lstrip("﻿"))


def lock():
    return threading.Lock()  # type: ignore[attr-defined]
