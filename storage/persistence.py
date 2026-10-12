from datetime import datetime

from entities.base import BaseEntity
from entities.team import Team
from entities.user import User
from entities.work_session import WorkSession


class PersistenceService(BaseEntity):
    def __init__(self, path: str = "data.txt"):
        self._path = path
        self._sep = "\t"

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    def save(self, repository) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            for _key, t in repository.all_teams():
                f.write(self._sep.join(
                    ["TEAM", t.key, t.name, t.password, t.manager_login]
                ) + "\n")
            for _login, u in repository.all_users():
                f.write(self._sep.join(
                    ["USER", u.login, u.password, u.role, u.team_key or ""]
                ) + "\n")
            for s in repository.all_sessions():
                t_out = s.time_out.isoformat() if s.time_out else ""
                f.write(self._sep.join(
                    ["SESSION", s.user.login, s.time_in.isoformat(), t_out]
                ) + "\n")

    def load(self, repository) -> bool:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return False

        repository.clear()
        for line in lines:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split(self._sep)
            kind = parts[0]

            if kind == "TEAM" and len(parts) == 5:
                repository.add_team(Team(parts[1], parts[2], parts[3], parts[4]))
            elif kind == "USER" and len(parts) == 5:
                team_key = parts[4] if parts[4] else None
                repository.add_user(User(parts[1], parts[2], parts[3], team_key))
            elif kind == "SESSION" and len(parts) == 4:
                user = repository.get_user(parts[1])
                if user is None:
                    continue
                session = WorkSession(user, datetime.fromisoformat(parts[2]))
                if parts[3]:
                    session.time_out = datetime.fromisoformat(parts[3])
                repository.add_session(session)
        return True

    def display_info(self) -> str:
        return f"PersistenceService({self._path})"

    def __eq__(self, other) -> bool:
        return isinstance(other, PersistenceService) and self._path == other._path

    def __repr__(self) -> str:
        return f"PersistenceService({self._path!r})"

    def __str__(self) -> str:
        return self.display_info()