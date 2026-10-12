from entities.user import User
from entities.work_session import WorkSession
from storage.repository import WorkTimeRepository
from services.report_service import ReportService


if __name__ == "__main__":
    repo = WorkTimeRepository()

    u1 = repo.find_or_create_user("ivan")
    u2 = repo.find_or_create_user("anna")

    s1 = WorkSession(u1)
    repo.add_session(s1)
    repo.close_session(u1)

    s2 = WorkSession(u2)
    repo.add_session(s2)

    path = ReportService.save(repo.all_sessions(), "report.txt")
    print(f"Отчёт сохранён: {path}")
    print()
    print(ReportService.build_report(repo.all_sessions()))