import asyncio
import flet as ft

from storage.repository import WorkTimeRepository
from storage.persistence import PersistenceService
from entities.user import User
from entities.work_session import WorkSession


class AppState:
    def __init__(self):
        self.repository = WorkTimeRepository()
        self.persistence = PersistenceService("data.txt")
        loaded = self.persistence.load(self.repository)
        if not loaded:
            if self.repository.seed_default_team():
                self.persistence.save(self.repository)
        self.current_user: User | None = None

    def save(self):
        self.persistence.save(self.repository)


state = AppState()


def build_login_view(page: ft.Page) -> ft.View:
    login_field = ft.TextField(label="Логин", autofocus=True)
    password_field = ft.TextField(label="Пароль", password=True)
    error_text = ft.Text("", color=ft.Colors.RED)

    async def do_login(e):
        user = state.repository.authenticate(
            login_field.value.strip(), password_field.value
        )
        if user is None:
            error_text.value = "Неверный логин или пароль"
            page.update()
            return
        state.current_user = user
        await page.push_route("/main")

    return ft.View(
        route="/login",
        controls=[
            ft.AppBar(title=ft.Text("Вход в систему")),
            ft.Column(
                [
                    ft.Text("Учёт рабочего времени", size=24, weight=ft.FontWeight.BOLD),
                    login_field,
                    password_field,
                    ft.Button("Войти", on_click=do_login, width=300),  # ← ИЗМЕНЕНО
                    ft.TextButton(
                        "Зарегистрироваться",
                        on_click=lambda e: asyncio.create_task(
                            page.push_route("/register")
                        ),
                    ),
                    error_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )


def build_register_view(page: ft.Page) -> ft.View:
    role_dd = ft.Dropdown(
        label="Роль",
        options=[
            ft.DropdownOption(key="employee", text="Сотрудник"),  # ← ИЗМЕНЕНО
            ft.DropdownOption(key="manager", text="Руководитель"),  # ← ИЗМЕНЕНО
        ],
        value="employee",
    )
    login_field = ft.TextField(label="Логин")
    password_field = ft.TextField(label="Пароль", password=True)
    team_name_field = ft.TextField(label="Название команды")
    team_key_field = ft.TextField(label="Ключ команды")
    team_password_field = ft.TextField(label="Пароль команды", password=True)
    info_text = ft.Text("", color=ft.Colors.BLUE)

    def update_fields(e=None):
        is_manager = role_dd.value == "manager"
        team_name_field.visible = is_manager
        team_key_field.visible = not is_manager
        page.update()

    role_dd.on_change = update_fields

    async def do_register(e):
        login = login_field.value.strip()
        password = password_field.value
        team_password = team_password_field.value

        if not login or not password:
            info_text.value = "Заполните логин и пароль"
            page.update()
            return

        if role_dd.value == "manager":
            team_name = team_name_field.value.strip()
            if not team_name or not team_password:
                info_text.value = "Заполните название и пароль команды"
                page.update()
                return
            result = state.repository.register_manager(
                login, password, team_name, team_password
            )
            if result is None:
                info_text.value = "Логин уже занят"
                page.update()
                return
            user, team = result
            info_text.value = f"Команда создана. Ключ: {team.key}. Сохраните его!"
            page.update()
            page.show_dialog(ft.SnackBar(
                content=ft.Text(f"Ключ команды: {team.key}\nПередайте его сотрудникам.")
            ))
        else:
            team_key = team_key_field.value.strip()
            if not team_key or not team_password:
                info_text.value = "Заполните ключ и пароль команды"
                page.update()
                return
            user = state.repository.register_employee(
                login, password, team_key, team_password
            )
            if user is None:
                info_text.value = "Неверный ключ/пароль или логин занят"
                page.update()
                return

        state.save()
        state.current_user = user
        await page.push_route("/main")

    update_fields()

    return ft.View(
        route="/register",
        controls=[
            ft.AppBar(title=ft.Text("Регистрация")),
            ft.Column(
                [
                    role_dd,
                    login_field,
                    password_field,
                    team_name_field,
                    team_key_field,
                    team_password_field,
                    ft.Button("Зарегистрироваться", on_click=do_register, width=300),  # ← ИЗМЕНЕНО
                    ft.TextButton("Назад", on_click=lambda e: asyncio.create_task(
                        page.push_route("/login")
                    )),
                    info_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
        ],
    )


def build_main_view(page: ft.Page) -> ft.View:
    user = state.current_user
    if user is None:
        return ft.View(route="/main", controls=[ft.Text("Загрузка...")])

    is_manager = user.is_manager
    team = state.repository.find_team(user.team_key)
    team_name = team.name if team else "—"

    appbar = ft.AppBar(
        title=ft.Text(f"{user.login} — {'руководитель' if is_manager else 'сотрудник'}"),
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT,
                tooltip="Выйти из аккаунта",
                on_click=lambda e: asyncio.create_task(do_logout(page)),
            ),
        ],
    )

    controls = []

    if is_manager and team:
        controls.append(
            ft.Row(
                [
                    ft.Text(f"Ключ команды: {team.key}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                    ft.IconButton(
                        ft.Icons.COPY,
                        tooltip="Скопировать ключ",
                        on_click=lambda e: asyncio.create_task(copy_key(page, team.key)),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    if not is_manager:
        async def on_login(e):
            if state.repository.find_open_session(user) is not None:
                page.show_dialog(ft.SnackBar(content=ft.Text(f"{user.login} уже на смене")))
                return
            session = WorkSession(user)
            state.repository.add_session(session)
            state.save()
            page.show_dialog(ft.SnackBar(content=ft.Text(f"{user.login} вошёл в {session.time_in.strftime('%H:%M:%S')}")))
            refresh_table()

        async def on_logout(e):
            session = state.repository.close_session(user)
            if session is None:
                page.show_dialog(ft.SnackBar(content=ft.Text(f"{user.login} не на смене")))
                return
            state.save()
            page.show_dialog(ft.SnackBar(content=ft.Text(f"{user.login} вышел в {session.time_out.strftime('%H:%M:%S')}")))
            refresh_table()

        controls.append(
            ft.Row(
                [
                    ft.Button("Вход", on_click=on_login, expand=True),  # ← ИЗМЕНЕНО
                    ft.Button("Выход", on_click=on_logout, expand=True),  # ← ИЗМЕНЕНО
                ],
                spacing=10,
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("login")),
            ft.DataColumn(ft.Text("time_in")),
            ft.DataColumn(ft.Text("time_out")),
            ft.DataColumn(ft.Text("статус")),
        ],
        rows=[],
    )

    def refresh_table():
        if is_manager:
            sessions = list(state.repository.sessions_of_team(user.team_key))
        else:
            sessions = list(state.repository.sessions_of(user))
        table.rows.clear()
        fmt = "%d.%m.%Y %H:%M:%S"
        for s in sessions:
            status = "на смене" if s.time_out is None else "завершена"
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(s.user.login)),
                        ft.DataCell(ft.Text(s.time_in.strftime(fmt))),
                        ft.DataCell(ft.Text(s.time_out.strftime(fmt) if s.time_out else "")),
                        ft.DataCell(ft.Text(status)),
                    ]
                )
            )
        page.update()

    refresh_table()

    controls.append(ft.Text("Сессии:", weight=ft.FontWeight.BOLD))
    controls.append(ft.Row([table], scroll=ft.ScrollMode.AUTO))

    return ft.View(
        route="/main",
        appbar=appbar,
        controls=[
            ft.Column(
                controls,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
    )


async def do_logout(page: ft.Page):
    state.save()
    state.current_user = None
    await page.push_route("/login")


async def copy_key(page: ft.Page, key: str):
    await ft.Clipboard().set(key)
    page.show_dialog(ft.SnackBar(content=ft.Text(f"Ключ скопирован: {key}")))


def main(page: ft.Page):
    page.title = "Учёт рабочего времени"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.window.height = 800

    def route_change(e):
        page.views.clear()
        if page.route == "/login":
            page.views.append(build_login_view(page))
        elif page.route == "/register":
            page.views.append(build_register_view(page))
        elif page.route == "/main":
            if state.current_user is None:
                asyncio.create_task(page.push_route("/login"))
                return
            page.views.append(build_main_view(page))
        else:
            page.views.append(build_login_view(page))
        page.update()

    page.on_route_change = route_change
    asyncio.create_task(page.push_route("/login"))


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550, host="0.0.0.0")