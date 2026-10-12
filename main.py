from entities.user import User
from entities.work_session import WorkSession

from storage.repository import WorkTimeRepository


if __name__ == "__main__":
    repo = WorkTimeRepository()

    u1 = repo.find_or_create_user("ivan")
    u1_again = repo.find_or_create_user("ivan")
    u2 = repo.find_or_create_user("anna")

    print(u1 is u1_again)

    s1 = WorkSession(u1)
    repo.add_session(s1)

    print(repo.find_open_session(u1))
    print(repo.find_open_session(u2))

    repo.close_session(u1)
    print(repo.find_open_session(u1))

    print(repo)
    print(repo.all_sessions())