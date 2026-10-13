from datetime import datetime
from functools import total_ordering

from .base import BaseEntity
from .user import User


@total_ordering
class WorkSession(BaseEntity):
    def __init__(self, user: User, time_in: datetime | None = None):
        self._user = user
        self._time_in = time_in if time_in is not None else datetime.now()
        self._time_out: datetime | None = None

    @property
    def user(self) -> User:
        return self._user

    @user.setter
    def user(self, value: User) -> None:
        if not isinstance(value, User):
            raise TypeError("user должен быть объектом User")
        self._user = value

    @property
    def time_in(self) -> datetime:
        return self._time_in

    @time_in.setter
    def time_in(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError("time_in должен быть datetime")
        self._time_in = value

    @property
    def time_out(self) -> datetime | None:
        return self._time_out

    @time_out.setter
    def time_out(self, value: datetime | None) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError("time_out должен быть datetime или None")
        self._time_out = value

    def close(self) -> None:
        self._time_out = datetime.now()

    def display_info(self) -> str:
        out = self._time_out.strftime("%d.%m.%Y %H:%M:%S") if self._time_out else "—"
        return (
            f"{self._user.login}: "
            f"{self._time_in.strftime('%d.%m.%Y %H:%M:%S')} → {out}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, WorkSession):
            return NotImplemented
        return (self._user, self._time_in) == (other._user, other._time_in)

    def __lt__(self, other) -> bool:
        if not isinstance(other, WorkSession):
            return NotImplemented
        return (self._user.login, self._time_in) < (
            other._user.login,
            other._time_in,
        )

    def __repr__(self) -> str:
        return f"WorkSession({self._user!r}, {self._time_in!r}, {self._time_out!r})"

    def __str__(self) -> str:
        return self.display_info()
