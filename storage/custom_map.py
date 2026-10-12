from entities.base import BaseEntity


class CustomMap(BaseEntity):
    def __init__(self):
        self._items: list[tuple] = []

    @property
    def items(self) -> tuple:
        return tuple(self._items)

    @items.setter
    def items(self, value) -> None:
        self._items = list(value)

    def set(self, key, value) -> None:
        for i, (k, _) in enumerate(self._items):
            if k == key:
                self._items[i] = (key, value)
                return
        self._items.append((key, value))

    def get(self, key, default=None):
        for k, v in self._items:
            if k == key:
                return v
        return default

    def remove(self, key) -> bool:
        for i, (k, _) in enumerate(self._items):
            if k == key:
                del self._items[i]
                return True
        return False

    def contains(self, key) -> bool:
        return any(k == key for k, _ in self._items)

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()

    def display_info(self) -> str:
        pairs = ", ".join(f"{k!r}: {v!r}" for k, v in self._items)
        return f"CustomMap({pairs})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, CustomMap):
            return NotImplemented
        return self._items == other._items

    def __repr__(self) -> str:
        return f"CustomMap({self._items!r})"

    def __str__(self) -> str:
        return self.display_info()