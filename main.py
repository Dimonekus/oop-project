import sys
from PySide6.QtWidgets import QApplication

from storage.repository import WorkTimeRepository
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    repo = WorkTimeRepository()
    window = MainWindow(repo)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()