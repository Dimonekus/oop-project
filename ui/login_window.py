from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit

from storage.repository import WorkTimeRepository
from .widgets import MyLabel, MyLineEdit, MyPushButton


class LoginWindow(QWidget):
    login_successful = Signal(object)

    def __init__(self, repository: WorkTimeRepository):
        super().__init__()
        self._repository = repository
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(360, 260)

        layout = QVBoxLayout(self)

        title = MyLabel("Учёт рабочего времени")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        layout.addWidget(MyLabel("Логин:"))
        self.login_edit = MyLineEdit()
        self.login_edit.setPlaceholderText("admin или ivan, anna, ...")
        layout.addWidget(self.login_edit)

        layout.addWidget(MyLabel("Пароль:"))
        self.password_edit = MyLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("пароль = логин")
        layout.addWidget(self.password_edit)

        self.btn_login = MyPushButton("Войти")
        layout.addWidget(self.btn_login)

        self.error_label = MyLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #c0392b;")
        layout.addWidget(self.error_label)

        self.btn_login.clicked.connect(self._on_login)
        self.password_edit.returnPressed.connect(self._on_login)
        self.login_edit.returnPressed.connect(self._on_login)

    def _on_login(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text()

        user = self._repository.authenticate(login, password)
        if user is None:
            self.error_label.setText("Неверный логин или пароль")
            self.password_edit.clear()
            return

        self.error_label.setText("")
        self.login_successful.emit(user)