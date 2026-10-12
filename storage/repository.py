import secrets

from entities.base import BaseEntity
from entities.team import Team
from entities.user import User
from entities.work_session import WorkSession
from .custom_map import CustomMap


class WorkTimeRepository(BaseEntity):
    def __init__(self):
        self._users: CustomMap = CustomMap()      # login -> User
        self._teams: CustomMap = CustomMap()      # key   -> Team
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
    def teams(self) -> CustomMap:
        return self._teams

    @teams.setter
    def teams(self, value: CustomMap) -> None:
        if not isinstance(value, CustomMap):
            raise TypeError("teams должен быть CustomMap")
        self._teams = value

    @property
    def sessions(self) -> tuple:
        return tuple(self._sessions)

    @sessions.setter
    def sessions(self, value) -> None:
        self._sessions = list(value)

    def clear(self) -> None:
        self._users.clear()
        self._teams.clear()
        self._sessions = []

    def add_user(self, user: User) -> None:
        self._users.set(user.login, user)

    def add_team(self, team: Team) -> None:
        self._teams.set(team.key, team)

    def add_session(self, session: WorkSession) -> None:
        if not isinstance(session, WorkSession):
            raise TypeError("session должен быть WorkSession")
        self._sessions.append(session)

    def get_user(self, login: str) -> User | None:
        return self._users.get(login)

    def find_team(self, key: str) -> Team | None:
        return self._teams.get(key)

    def _generate_team_key(self) -> str:
        while True:
            key = secrets.token_hex(3).upper()  # например 'A3F91B'
            if self._teams.get(key) is None:
                return key

    def register_manager(self, login: str, password: str,
                         team_name: str, team_password: str) -> tuple[User, Team] | None:
        if self._users.get(login) is not None:
            return None
        key = self._generate_team_key()
        team = Team(key, team_name, team_password, login)
        user = User(login, password, User.ROLE_MANAGER, key)
        self._teams.set(key, team)
        self._users.set(login, user)
        return user, team

    def register_employee(self, login: str, password: str,
                          team_key: str, team_password: str) -> User | None:
        if self._users.get(login) is not None:
            return None
        team = self._teams.get(team_key)
        if team is None:
            return None
        if not team.check_password(team_password):
            return None
        user = User(login, password, User.ROLE_EMPLOYEE, team_key)
        self._users.set(login, user)
        return user

    def authenticate(self, login: str, password: str) -> User | None:
        user = self._users.get(login)
        if user is None or not user.check_password(password):
            return None
        return user

    def users_of_team(self, team_key: str) -> tuple:
        return tuple(
            (login, user) for login, user in self._users.items
            if user.team_key == team_key
        )

    def sessions_of_team(self, team_key: str) -> tuple:
        return tuple(
            s for s in self._sessions if s.user.team_key == team_key
        )

    def sessions_of(self, user: User) -> tuple:
        return tuple(s for s in self._sessions if s.user == user)

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

    def all_teams(self) -> tuple:
        return tuple(self._teams.items)

    def display_info(self) -> str:
        return (f"WorkTimeRepository: {self._users.size()} польз., "
                f"{self._teams.size()} команд, {len(self._sessions)} сессий")

    def __eq__(self, other) -> bool:
        if not isinstance(other, WorkTimeRepository):
            return NotImplemented
        return (self._users, self._teams, self._sessions) == \
               (other._users, other._teams, other._sessions)

    def __repr__(self) -> str:
        return f"WorkTimeRepository(users={self._users!r}, teams={self._teams!r})"

    def __str__(self) -> str:
        return self.display_info()