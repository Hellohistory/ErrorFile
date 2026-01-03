from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Optional, Tuple


class InspectionCache:
    def __init__(self, max_entries: int = 1024):
        self._max_entries = max_entries
        self._entries: "OrderedDict[Tuple[Any, ...], Any]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: Tuple[Any, ...]) -> Optional[Any]:
        with self._lock:
            value = self._entries.get(key)
            if value is not None:
                self._entries.move_to_end(key)
            return value

    def set(self, key: Tuple[Any, ...], value: Any) -> None:
        with self._lock:
            if key in self._entries:
                self._entries.move_to_end(key)
            self._entries[key] = value
            if len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)
