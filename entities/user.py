from functools import total_ordering
from datetime import datetime

from .base import BaseEntity


@total_ordering
class User(BaseEntity):
    def __init__(self, login: str):
        self._login = login

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Логин не может быть пустым")
        self._login = value.strip()

    def display_info(self) -> str:
        return f"Пользователь: {self._login}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._login == other._login

    def __lt__(self, other) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._login < other._login

    def __repr__(self) -> str:
        return f"User({self._login!r})"

    def __str__(self) -> str:
        return self._login