from entities.user import User
from entities.work_session import WorkSession
from storage.custom_map import CustomMap


if __name__ == "__main__":
    u = User("ivan")
    s = WorkSession(u)
    s.close()

    m = CustomMap()
    m.set("ivan", s)
    m.set("anna", None)

    print(m)
    print(m.get("ivan"))
    print(m.get("petr", "нет"))
    print(m.contains("anna"))
    print(m.size())
    m.set("anna", s)
    print(m.get("anna"))