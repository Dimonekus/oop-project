import sys
from PySide6.QtWidgets import QApplication

from storage.repository import WorkTimeRepository
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


class Application:
    def __init__(self, repository: WorkTimeRepository):
        self._repository = repository
        self._login_window: LoginWindow | None = None
        self._main_window: MainWindow | None = None

    def start(self):
        self._login_window = LoginWindow(self._repository)
        self._login_window.login_successful.connect(self._on_login_success)
        self._login_window.show()

    def _on_login_success(self, user):
        self._main_window = MainWindow(self._repository, user)
        self._main_window.show()
        self._login_window.close()


def main():
    app = QApplication(sys.argv)
    application = Application(WorkTimeRepository())
    application.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()