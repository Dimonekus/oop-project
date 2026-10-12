from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QRadioButton, QMessageBox,
)

from storage.repository import WorkTimeRepository
from .widgets import MyLabel, MyLineEdit, MyPushButton


class RegisterWindow(QWidget):
    registered = Signal(object)   # User

    def __init__(self, repository: WorkTimeRepository):
        super().__init__()
        self._repository = repository
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Регистрация")
        self.setFixedSize(420, 460)

        layout = QVBoxLayout(self)

        title = MyLabel("Регистрация")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        layout.addWidget(MyLabel("Роль:"))
        role_layout = QHBoxLayout()
        self.radio_manager = QRadioButton("Руководитель")
        self.radio_employee = QRadioButton("Сотрудник")
        self.radio_employee.setChecked(True)
        role_layout.addWidget(self.radio_employee)
        role_layout.addWidget(self.radio_manager)
        role_layout.addStretch()
        layout.addLayout(role_layout)

        layout.addWidget(MyLabel("Логин:"))
        self.login_edit = MyLineEdit()
        layout.addWidget(self.login_edit)

        layout.addWidget(MyLabel("Пароль:"))
        self.password_edit = MyLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        self.team_name_label = MyLabel("Название команды:")
        self.team_name_edit = MyLineEdit()
        layout.addWidget(self.team_name_label)
        layout.addWidget(self.team_name_edit)

        self.team_key_label = MyLabel("Ключ команды:")
        self.team_key_edit = MyLineEdit()
        layout.addWidget(self.team_key_label)
        layout.addWidget(self.team_key_edit)

        self.team_password_label = MyLabel("Пароль команды:")
        self.team_password_edit = MyLineEdit()
        self.team_password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.team_password_label)
        layout.addWidget(self.team_password_edit)

        self.btn_register = MyPushButton("Зарегистрироваться")
        layout.addWidget(self.btn_register)

        self.info_label = MyLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.radio_manager.toggled.connect(self._update_fields)
        self.btn_register.clicked.connect(self._on_register)
        self._update_fields()

    def _update_fields(self):
        is_manager = self.radio_manager.isChecked()
        self.team_name_label.setVisible(is_manager)
        self.team_name_edit.setVisible(is_manager)
        self.team_key_label.setVisible(not is_manager)
        self.team_key_edit.setVisible(not is_manager)

    def _on_register(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        team_password = self.team_password_edit.text()

        if not login or not password:
            self.info_label.setText("Заполните логин и пароль")
            return

        if self.radio_manager.isChecked():
            team_name = self.team_name_edit.text().strip()
            if not team_name or not team_password:
                self.info_label.setText("Заполните название и пароль команды")
                return
            result = self._repository.register_manager(
                login, password, team_name, team_password
            )
            if result is None:
                self.info_label.setText("Логин уже занят")
                return
            user, team = result
            QMessageBox.information(
                self, "Команда создана",
                f"Ключ вашей команды: {team.key}\n\n"
                f"Передайте его сотрудникам вместе с паролем команды."
            )
        else:
            team_key = self.team_key_edit.text().strip()
            if not team_key or not team_password:
                self.info_label.setText("Заполните ключ и пароль команды")
                return
            user = self._repository.register_employee(
                login, password, team_key, team_password
            )
            if user is None:
                self.info_label.setText("Неверный ключ/пароль или логин занят")
                return

        self.info_label.setText("")
        self.registered.emit(user)