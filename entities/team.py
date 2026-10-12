from functools import total_ordering

from .base import BaseEntity


@total_ordering
class Team(BaseEntity):
    def __init__(self, key: str, name: str, password: str, manager_login: str):
        self._key = key
        self._name = name
        self._password = password
        self._manager_login = manager_login

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        if not value:
            raise ValueError("Ключ команды не может быть пустым")
        self._key = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Название команды не может быть пустым")
        self._name = value.strip()

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        if not value:
            raise ValueError("Пароль команды не может быть пустым")
        self._password = value

    @property
    def manager_login(self) -> str:
        return self._manager_login

    @manager_login.setter
    def manager_login(self, value: str) -> None:
        self._manager_login = value

    def check_password(self, raw: str) -> bool:
        return self._password == raw

    def display_info(self) -> str:
        return f"Команда «{self._name}» (ключ {self._key})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Team):
            return NotImplemented
        return self._key == other._key

    def __lt__(self, other) -> bool:
        if not isinstance(other, Team):
            return NotImplemented
        return self._key < other._key

    def __repr__(self) -> str:
        return f"Team({self._key!r}, {self._name!r})"

    def __str__(self) -> str:
        return self._name