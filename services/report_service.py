from datetime import datetime

from entities.base import BaseEntity
from entities.work_session import WorkSession


class ReportService(BaseEntity):
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

    def display_info(self) -> str:
        return "ReportService — сохранение отчёта"

    @staticmethod
    def _fmt(dt: datetime | None) -> str:
        if dt is None:
            return ""
        return dt.strftime(ReportService.TIME_FORMAT)

    @staticmethod
    def build_report(sessions: list[WorkSession] | tuple) -> str:
        headers = ("login", "time_in", "time_out")
        widths = (12, 21, 21)

        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

        def row(values):
            cells = []
            for value, w in zip(values, widths):
                cells.append(f" {value:<{w}} ")
            return "|" + "|".join(cells) + "|"

        lines = [sep, row(headers), sep]
        for s in sessions:
            lines.append(row((
                s.user.login,
                ReportService._fmt(s.time_in),
                ReportService._fmt(s.time_out),
            )))
        lines.append(sep)
        return "\n".join(lines)

    @staticmethod
    def save(sessions, path: str = "report.txt") -> str:
        text = ReportService.build_report(sessions)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def __eq__(self, other) -> bool:
        return isinstance(other, ReportService)

    def __repr__(self) -> str:
        return "ReportService()"

    def __str__(self) -> str:
        return self.display_info()