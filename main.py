from entities.user import User
from entities.work_session import WorkSession


if __name__ == "__main__":
    u = User("ivan")
    s = WorkSession(u)
    s.close()
    print(s)