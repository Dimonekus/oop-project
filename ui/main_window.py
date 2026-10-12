from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem,
)

from entities.user import User
from entities.work_session import WorkSession
from storage.repository import WorkTimeRepository
from services.report_service import ReportService

from .widgets import (
    MyLabel, MyLineEdit, MyPushButton, MyTableWidget, MyListWidget,
    MyComboBox, MyCheckBox, MyTextEdit, MyStatusBar, MyWidget,
)


class MainWindow(QMainWindow):
    def __init__(self, repository: WorkTimeRepository, current_user: User):
        super().__init__()
        self._repository = repository
        self._current_user = current_user
        self._build_ui()
        self._refresh_users_list()
        self._refresh_table()

    def _build_ui(self):
        role = "руководитель" if self._current_user.is_manager else "сотрудник"
        self.setWindowTitle(f"Учёт рабочего времени — {self._current_user.login} ({role})")
        self.resize(900, 600)

        central = MyWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        title = MyLabel(f"Вы вошли как: {self._current_user.login} ({role})")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        main_layout.addWidget(title)

        controls = QHBoxLayout()

        if self._current_user.is_manager:
            controls.addWidget(MyLabel("Логин:"))
            self.login_edit = MyLineEdit()
            self.login_edit.setPlaceholderText("любой сотрудник")
            self.login_edit.setAlignment(Qt.AlignCenter)
            controls.addWidget(self.login_edit)
        else:
            controls.addWidget(MyLabel("Сотрудник:"))
            self.login_edit = MyLineEdit()
            self.login_edit.setText(self._current_user.login)
            self.login_edit.setReadOnly(True)
            self.login_edit.setAlignment(Qt.AlignCenter)
            controls.addWidget(self.login_edit)

        self.btn_in = MyPushButton("Вход")
        self.btn_out = MyPushButton("Выход")
        controls.addWidget(self.btn_in)
        controls.addWidget(self.btn_out)
        main_layout.addLayout(controls)

        if self._current_user.is_manager:
            filters = QHBoxLayout()
            self.check_active = MyCheckBox("Только открытые сессии")
            self.combo_user = MyComboBox()
            self.combo_user.addItem("Все пользователи")

            filters.addWidget(self.check_active)
            filters.addWidget(MyLabel("Фильтр:"))
            filters.addWidget(self.combo_user)
            filters.addStretch()
            main_layout.addLayout(filters)
        else:
            self.check_active = None
            self.combo_user = None

        content = QHBoxLayout()

        if self._current_user.is_manager:
            self.users_list = MyListWidget()
            self.users_list.setFixedWidth(180)
            self.users_list.itemClicked.connect(self.on_user_picked)
            content.addWidget(self.users_list)
        else:
            self.users_list = None

        self.table = MyTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["login", "time_in", "time_out", "статус"]
        )
        content.addWidget(self.table)
        main_layout.addLayout(content)

        self.log = MyTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(100)
        main_layout.addWidget(MyLabel("Журнал действий:"))
        main_layout.addWidget(self.log)

        self.status = MyStatusBar()
        self.setStatusBar(self.status)

        self.btn_in.clicked.connect(self.on_login)
        self.btn_out.clicked.connect(self.on_logout)
        if self.check_active is not None:
            self.check_active.stateChanged.connect(self._refresh_table)
        if self.combo_user is not None:
            self.combo_user.currentIndexChanged.connect(self._refresh_table)

        self._log("Приложение запущено")

    def _log(self, text: str):
        self.log.append(text)
        self.status.showMessage(text, 3000)

    def on_login(self):
        user = self._resolve_target_user()
        if user is None:
            return
        if self._repository.find_open_session(user) is not None:
            self._log(f"{user.login} уже на смене")
            return

        session = WorkSession(user)
        self._repository.add_session(session)
        self._log(f"{user.login} вошёл в {session.time_in.strftime('%H:%M:%S')}")

        self._refresh_table()

    def on_logout(self):
        user = self._resolve_target_user()
        if user is None:
            return
        session = self._repository.close_session(user)
        if session is None:
            self._log(f"{user.login} не на смене")
            return

        self._log(f"{user.login} вышел в {session.time_out.strftime('%H:%M:%S')}")
        self._refresh_table()

    def _resolve_target_user(self) -> User | None:
        if self._current_user.is_manager:
            login = self.login_edit.text().strip()
            if not login:
                self._log("Ошибка: пустой логин")
                return None
            user = self._repository.get_user(login)
            if user is None:
                self._log(f"Пользователь {login} не найден")
                return None
            return user
        return self._current_user

    def on_user_picked(self, item):
        self.login_edit.setText(item.text())

    def _refresh_users_list(self):
        if self.users_list is None:
            return
        self.users_list.clear()
        self.combo_user.blockSignals(True)
        current = self.combo_user.currentText()
        self.combo_user.clear()
        self.combo_user.addItem("Все пользователи")

        for login, _user in self._repository.all_users():
            self.users_list.addItem(login)
            self.combo_user.addItem(login)

        idx = self.combo_user.findText(current)
        self.combo_user.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_user.blockSignals(False)

    def _refresh_table(self):
        if self._current_user.is_manager:
            sessions = list(self._repository.all_sessions())
        else:
            sessions = list(self._repository.sessions_of(self._current_user))

        if self.check_active is not None and self.check_active.isChecked():
            sessions = [s for s in sessions if s.time_out is None]
        if self.combo_user is not None:
            user_filter = self.combo_user.currentText()
            if user_filter and user_filter != "Все пользователи":
                sessions = [s for s in sessions if s.user.login == user_filter]

        self.table.setRowCount(len(sessions))
        fmt = "%d.%m.%Y %H:%M:%S"
        for row, s in enumerate(sessions):
            status = "на смене" if s.time_out is None else "завершена"
            values = [
                s.user.login,
                s.time_in.strftime(fmt),
                s.time_out.strftime(fmt) if s.time_out else "",
                status,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def closeEvent(self, event):
        ReportService.save(list(self._repository.all_sessions()), "report.txt")
        super().closeEvent(event)