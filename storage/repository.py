from entities.base import BaseEntity
from entities.user import User
from entities.work_session import WorkSession

from .custom_map import CustomMap


class WorkTimeRepository(BaseEntity):
    def __init__(self):
        self._users: CustomMap = CustomMap()
        self._sessions: list[WorkSession] = []

    @property
    def users(self) -> CustomMap:
        return self._users

    @users.setter
    def users(self, value: CustomMap) -> None:
        if not isinstance(value, CustomMap):
            raise TypeError("users должен быть CustomMap")
        self._users = value

    @property
    def sessions(self) -> tuple:
        return tuple(self._sessions)

    @sessions.setter
    def sessions(self, value) -> None:
        self._sessions = list(value)

    def find_or_create_user(self, login: str) -> User:
        existing = self._users.get(login)
        if existing is not None:
            return existing
        user = User(login)
        self._users.set(login, user)
        return user

    def add_session(self, session: WorkSession) -> None:
        if not isinstance(session, WorkSession):
            raise TypeError("session должен быть WorkSession")
        self._sessions.append(session)

    def find_open_session(self, user: User) -> WorkSession | None:
        for s in self._sessions:
            if s.user == user and s.time_out is None:
                return s
        return None

    def close_session(self, user: User) -> WorkSession | None:
        session = self.find_open_session(user)
        if session is not None:
            session.close()
        return session

    def all_sessions(self) -> tuple:
        return tuple(self._sessions)

    def all_users(self) -> tuple:
        return tuple(self._users.items)

    def display_info(self) -> str:
        return f"WorkTimeRepository: {self._users.size()} польз., {len(self._sessions)} сессий"

    def __eq__(self, other) -> bool:
        if not isinstance(other, WorkTimeRepository):
            return NotImplemented
        return (self._users, self._sessions) == (other._users, other._sessions)

    def __repr__(self) -> str:
        return f"WorkTimeRepository(users={self._users!r}, sessions={self._sessions!r})"

    def __str__(self) -> str:
        return self.display_info()