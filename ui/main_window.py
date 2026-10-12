from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QApplication,
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
    logout_requested = Signal()

    def __init__(self, repository: WorkTimeRepository, current_user: User):
        super().__init__()
        self._repository = repository
        self._current_user = current_user
        self._team = repository.find_team(current_user.team_key)
        self._build_ui()
        self._refresh_users_list()
        self._refresh_table()

    def _build_ui(self):
        user = self._current_user
        is_manager = user.is_manager
        role_text = "руководитель" if is_manager else "сотрудник"
        team_text = self._team.name if self._team else "—"

        self.setWindowTitle(f"Учёт рабочего времени — {user.login} ({role_text})")
        self.resize(960, 640)

        central = MyWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        top = QHBoxLayout()
        title = MyLabel(f"{user.login} — {role_text}, команда «{team_text}»")
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 4px;")
        top.addWidget(title)
        top.addStretch()
        self.btn_logout = MyPushButton("Выйти из аккаунта")
        top.addWidget(self.btn_logout)
        main_layout.addLayout(top)

        if is_manager and self._team:
            key_layout = QHBoxLayout()

            self.key_label = MyLabel(f"Ключ команды: {self._team.key}")
            self.key_label.setStyleSheet(
                "padding: 6px; color: #2a6df4; font-weight: bold;"
            )
            key_layout.addWidget(self.key_label)
            key_layout.addStretch()

            self.btn_copy_key = MyPushButton("Скопировать ключ")
            self.btn_copy_key.clicked.connect(self._copy_key)
            key_layout.addWidget(self.btn_copy_key)

            main_layout.addLayout(key_layout)
        else:
            self.key_label = None
            self.btn_copy_key = None

        if not is_manager:
            controls = QHBoxLayout()
            controls.addWidget(MyLabel("Я:"))
            self.login_edit = MyLineEdit()
            self.login_edit.setText(user.login)
            self.login_edit.setReadOnly(True)
            self.login_edit.setAlignment(Qt.AlignCenter)
            controls.addWidget(self.login_edit)

            self.btn_in = MyPushButton("Вход")
            self.btn_out = MyPushButton("Выход")
            controls.addWidget(self.btn_in)
            controls.addWidget(self.btn_out)
            main_layout.addLayout(controls)
        else:
            info = MyLabel("Режим просмотра: вы видите сессии своей команды.")
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("color: #555; padding: 6px;")
            main_layout.addWidget(info)
            self.login_edit = None
            self.btn_in = None
            self.btn_out = None

        filters = QHBoxLayout()
        self.check_active = MyCheckBox("Только открытые сессии")
        self.combo_user = MyComboBox()
        self.combo_user.addItem("Все сотрудники")
        filters.addWidget(self.check_active)
        filters.addWidget(MyLabel("Фильтр:"))
        filters.addWidget(self.combo_user)
        filters.addStretch()
        main_layout.addLayout(filters)

        content = QHBoxLayout()
        self.users_list = MyListWidget()
        self.users_list.setFixedWidth(180)
        content.addWidget(self.users_list)

        self.table = MyTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["login", "time_in", "time_out", "статус"]
        )
        content.addWidget(self.table)
        main_layout.addLayout(content)

        self.log = MyTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(90)
        main_layout.addWidget(MyLabel("Журнал действий:"))
        main_layout.addWidget(self.log)

        self.status = MyStatusBar()
        self.setStatusBar(self.status)

        self.btn_logout.clicked.connect(lambda: self.logout_requested.emit())
        if self.btn_in is not None:
            self.btn_in.clicked.connect(self.on_login)
            self.btn_out.clicked.connect(self.on_logout)
        self.users_list.itemClicked.connect(self.on_user_picked)
        self.check_active.stateChanged.connect(self._refresh_table)
        self.combo_user.currentIndexChanged.connect(self._refresh_table)

        self._log("Приложение запущено")

    def _log(self, text: str):
        self.log.append(text)
        self.status.showMessage(text, 3000)

    def on_login(self):
        user = self._current_user
        if self._repository.find_open_session(user) is not None:
            self._log(f"{user.login} уже на смене")
            return
        session = WorkSession(user)
        self._repository.add_session(session)
        self._log(f"{user.login} вошёл в {session.time_in.strftime('%H:%M:%S')}")
        self._refresh_table()

    def on_logout(self):
        user = self._current_user
        session = self._repository.close_session(user)
        if session is None:
            self._log(f"{user.login} не на смене")
            return
        self._log(f"{user.login} вышел в {session.time_out.strftime('%H:%M:%S')}")
        self._refresh_table()

    def on_user_picked(self, item):
        idx = self.combo_user.findText(item.text())
        if idx >= 0:
            self.combo_user.setCurrentIndex(idx)

    def _copy_key(self):
        if self._team is None:
            return
        QApplication.clipboard().setText(self._team.key)
        self._log(f"Ключ команды скопирован: {self._team.key}")

    def _team_key(self) -> str:
        return self._current_user.team_key or ""

    def _refresh_users_list(self):
        self.users_list.clear()
        self.combo_user.blockSignals(True)
        current = self.combo_user.currentText()
        self.combo_user.clear()
        self.combo_user.addItem("Все сотрудники")

        for login, user in self._repository.users_of_team(self._team_key()):
            if user == self._current_user:
                continue
            self.users_list.addItem(login)
            self.combo_user.addItem(login)

        idx = self.combo_user.findText(current)
        self.combo_user.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_user.blockSignals(False)

    def _refresh_table(self):
        if self._current_user.is_manager:
            sessions = list(self._repository.sessions_of_team(self._team_key()))
        else:
            sessions = list(self._repository.sessions_of(self._current_user))

        if self.check_active.isChecked():
            sessions = [s for s in sessions if s.time_out is None]

        user_filter = self.combo_user.currentText()
        if user_filter and user_filter != "Все сотрудники":
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