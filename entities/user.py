from functools import total_ordering

from .base import BaseEntity


@total_ordering
class User(BaseEntity):
    ROLE_MANAGER = "manager"
    ROLE_EMPLOYEE = "employee"

    def __init__(self, login: str, password: str, role: str = ROLE_EMPLOYEE):
        self._login = login
        self._password = password
        self._role = role

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Логин не может быть пустым")
        self._login = value.strip()

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        if not value:
            raise ValueError("Пароль не может быть пустым")
        self._password = value

    @property
    def role(self) -> str:
        return self._role

    @role.setter
    def role(self, value: str) -> None:
        if value not in (self.ROLE_MANAGER, self.ROLE_EMPLOYEE):
            raise ValueError("Недопустимая роль")
        self._role = value

    @property
    def is_manager(self) -> bool:
        return self._role == self.ROLE_MANAGER

    def check_password(self, raw: str) -> bool:
        return self._password == raw

    def display_info(self) -> str:
        role = "руководитель" if self.is_manager else "сотрудник"
        return f"{self._login} ({role})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._login == other._login

    def __lt__(self, other) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._login < other._login

    def __repr__(self) -> str:
        return f"User({self._login!r}, role={self._role!r})"

    def __str__(self) -> str:
        return self._login