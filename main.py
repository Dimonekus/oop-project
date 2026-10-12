import sys
from PySide6.QtWidgets import QApplication

from storage.repository import WorkTimeRepository
from storage.persistence import PersistenceService
from ui.login_window import LoginWindow
from ui.register_window import RegisterWindow
from ui.main_window import MainWindow


class Application:
    def __init__(self, repository: WorkTimeRepository):
        self._repository = repository
        self._persistence = PersistenceService("data.txt")

        self._login_window: LoginWindow | None = None
        self._register_window: RegisterWindow | None = None
        self._main_window: MainWindow | None = None

        loaded = self._persistence.load(repository)
        if not loaded:
            if self._repository.seed_default_team():
                self._persistence.save(self._repository)

    def start(self):
        self._show_login()

    def save(self):
        self._persistence.save(self._repository)

    def _show_login(self):
        self._login_window = LoginWindow(self._repository)
        self._login_window.login_successful.connect(self._on_login_success)
        self._login_window.register_requested.connect(self._show_register)
        self._login_window.show()

    def _show_register(self):
        self._register_window = RegisterWindow(self._repository)
        self._register_window.registered.connect(self._on_login_success)
        self._register_window.show()

    def _on_login_success(self, user):
        self._main_window = MainWindow(self._repository, user)
        self._main_window.logout_requested.connect(self._on_logout)
        self._main_window.show()
        self._close_login_and_register()
        self.save()

    def _on_logout(self):
        self.save()
        if self._main_window is not None:
            self._main_window.close()
            self._main_window = None
        self._show_login()

    def _close_login_and_register(self):
        if self._login_window is not None:
            self._login_window.close()
            self._login_window = None
        if self._register_window is not None:
            self._register_window.close()
            self._register_window = None


def main():
    app = QApplication(sys.argv)
    application = Application(WorkTimeRepository())
    app.aboutToQuit.connect(application.save)
    application.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()