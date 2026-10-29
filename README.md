# Time Tracking

Практическое задание к лекции №5 «Этапы разработки программного продукта».

## Назначение

Модуль добавляет в систему задач из лекции (`Task`, `User`, `TaskManager`) учет времени:
запуск и остановку таймера, подсчет затраченного времени и отчет.

## Файлы

| Файл | Содержимое |
|---|---|
| `task_system.py` | существующая система задач из лекции |
| `time_tracking.py` | модуль учета времени |
| `test_time_tracking.py` | unit-тесты |

## Требования и реализация

| № | Требование | Реализация |
|---|---|---|
| 1 | Старт/остановка таймера для задачи | `start_timer(task_id, user_id)`, `stop_timer(task_id)` |
| 2 | Учет общего затраченного времени | `get_task_time(task_id)` |
| 3 | Генерация отчетов по времени | `generate_report()` |
| 4 | Интеграция с системой задач | `TimeTrackedTaskManager` — наследник `TaskManager` |

## Классы

- `TimeEntry` — один интервал работы (задача, пользователь, начало, конец). Пока конец не задан, таймер идет.
- `TimeTracker` — логика учета; получает `TaskManager` и функцию часов `clock` (по умолчанию `datetime.now`, в тестах подменяется).
- `TimeTrackedTaskManager` — `TaskManager` с подключенным учетом времени; старые методы работают как раньше.

Ошибки (`ValueError`): задача или пользователь не найдены, таймер уже запущен, таймер не запущен.

## Пример

```python
from datetime import datetime, timedelta
from task_system import Priority
from time_tracking import TimeTrackedTaskManager

manager = TimeTrackedTaskManager()
user = manager.create_user("Алексей", "alexey@company.com")
task = manager.create_task("REST API", "Описание", Priority.HIGH,
                           datetime.now() + timedelta(days=7))

manager.start_timer(task.task_id, user.user_id)
# ... работа ...
manager.stop_timer(task.task_id)

print(manager.tracker.get_task_time(task.task_id))  # timedelta
print(manager.get_time_report())
# {'total': '00:45:00', 'by_task': {'REST API': '00:45:00'}, 'by_user': {'Алексей': '00:45:00'}}
```

## Тестирование

```bash
python3 -m unittest -v
```

11 тестов, покрытие `time_tracking.py` — 100 %. Тесты используют управляемые часы
`FakeClock`, поэтому не ждут реальное время.
