# time_tracking.py
"""Модуль учета времени для системы управления задачами.

Требования задания:
    1. Старт/остановка таймера для задачи  -> start_timer, stop_timer
    2. Учет общего затраченного времени    -> get_task_time
    3. Генерация отчетов по времени        -> generate_report
    4. Интеграция с системой задач         -> TimeTrackedTaskManager
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional

from task_system import TaskManager


@dataclass
class TimeEntry:
    """Один интервал работы над задачей. Пока end is None, таймер идет."""
    task_id: int
    user_id: int
    start: datetime
    end: Optional[datetime] = None


class TimeTracker:
    """Учет времени. clock - функция текущего времени (в тестах подменяется)."""

    def __init__(self, task_manager: TaskManager,
                 clock: Callable[[], datetime] = datetime.now):
        self.task_manager = task_manager
        self.clock = clock
        self.entries = []

    def start_timer(self, task_id: int, user_id: int) -> TimeEntry:
        """Запускает таймер для задачи."""
        if task_id not in self.task_manager.tasks:
            raise ValueError(f"Задача {task_id} не найдена")
        if user_id not in self.task_manager.users:
            raise ValueError(f"Пользователь {user_id} не найден")
        if self._running_entry(task_id):
            raise ValueError(f"Таймер задачи {task_id} уже запущен")
        entry = TimeEntry(task_id, user_id, self.clock())
        self.entries.append(entry)
        return entry

    def stop_timer(self, task_id: int) -> TimeEntry:
        """Останавливает таймер задачи."""
        entry = self._running_entry(task_id)
        if entry is None:
            raise ValueError(f"Таймер задачи {task_id} не запущен")
        entry.end = self.clock()
        return entry

    def get_task_time(self, task_id: int) -> timedelta:
        """Общее время по задаче (идущий таймер считается до текущего момента)."""
        return sum((self._duration(e) for e in self.entries
                    if e.task_id == task_id), timedelta())

    def generate_report(self) -> Dict:
        """Отчет: время по каждой задаче, по каждому пользователю и всего."""
        by_task, by_user = {}, {}
        for e in self.entries:
            title = self.task_manager.tasks[e.task_id].title
            name = self.task_manager.users[e.user_id].name
            by_task[title] = by_task.get(title, timedelta()) + self._duration(e)
            by_user[name] = by_user.get(name, timedelta()) + self._duration(e)
        return {
            "total": format_duration(sum(by_task.values(), timedelta())),
            "by_task": {k: format_duration(v) for k, v in by_task.items()},
            "by_user": {k: format_duration(v) for k, v in by_user.items()},
        }

    def _running_entry(self, task_id: int) -> Optional[TimeEntry]:
        for e in self.entries:
            if e.task_id == task_id and e.end is None:
                return e
        return None

    def _duration(self, entry: TimeEntry) -> timedelta:
        return (entry.end or self.clock()) - entry.start


def format_duration(duration: timedelta) -> str:
    """timedelta -> 'ЧЧ:ММ:СС'."""
    hours, rest = divmod(int(duration.total_seconds()), 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class TimeTrackedTaskManager(TaskManager):
    """TaskManager из лекции + учет времени (старый код работает без изменений)."""

    def __init__(self, clock: Callable[[], datetime] = datetime.now):
        super().__init__()
        self.tracker = TimeTracker(self, clock)

    def start_timer(self, task_id: int, user_id: int) -> TimeEntry:
        return self.tracker.start_timer(task_id, user_id)

    def stop_timer(self, task_id: int) -> TimeEntry:
        return self.tracker.stop_timer(task_id)

    def get_time_report(self) -> Dict:
        return self.tracker.generate_report()
