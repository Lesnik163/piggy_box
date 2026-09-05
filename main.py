"""Консольное меню приложения «Копилка»."""

import sys


def _configure_console_encoding():
    """Windows-терминал часто не UTF-8 — без этого кириллица ломается при вводе и выводе."""
    if sys.platform != "win32":
        return
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


_configure_console_encoding()

from models.constants import STATUSES
from services import goal_service as gs
from utils.date_utils import format_date, parse_date


MENU = """
==================================================
           КОПИЛКА — управление накоплениями
==================================================
  1. Добавить цель
  2. Список целей
  3. Прогресс по цели
  4. Пополнить баланс
  5. Снять с баланса
  6. Изменить статус
  7. Удалить цель
  8. Общий прогресс
  9. Цели по категории
 10. Напоминания о сроках
 11. Прогноз даты завершения
 12. Изменить срок цели
  0. Выход
==================================================
"""


def read_text(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("Значение не может быть пустым.")
    return value


def read_amount(prompt):
    raw = input(prompt).strip().replace(",", ".")
    try:
        amount = float(raw)
    except ValueError as exc:
        raise ValueError("Нужно ввести число, например 1500 или 1500.50.") from exc
    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля.")
    return amount


def read_int(prompt, minimum, maximum):
    raw = input(prompt).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("Нужно ввести целое число.") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"Введите число от {minimum} до {maximum}.")
    return value


def read_optional_date(prompt):
    """Пустой ввод — даты нет. Иначе разбираем ДД.ММ.ГГГГ."""
    raw = input(prompt).strip()
    if not raw:
        return None
    return parse_date(raw)


def pick_goal_name():
    if not gs.goals:
        raise ValueError("Сначала добавьте хотя бы одну цель.")
    for index, goal in enumerate(gs.goals, start=1):
        print(f"  {index}. {goal}")
    index = read_int("Номер цели: ", 1, len(gs.goals))
    return gs.goals[index - 1].name


def print_goals(goal_list):
    if not goal_list:
        print("Целей нет.")
        return
    for index, goal in enumerate(goal_list, start=1):
        print(f"{index}. {goal} [{goal.category}] срок: {format_date(goal.deadline)}")


def add_goal_action():
    name = read_text("Название цели: ")
    target = read_amount("Итоговая сумма: ")
    category = read_text("Категория: ")
    deadline = read_optional_date("Дата завершения ДД.ММ.ГГГГ (Enter — пропустить): ")
    goal = gs.add_goal(name, target, category, deadline=deadline)
    print(f"Цель «{goal.name}» добавлена. Срок: {format_date(goal.deadline)}.")


def list_goals_action():
    print_goals(gs.goals)


def show_progress_action():
    name = pick_goal_name()
    gs.find_goal(name).show_progress()


def deposit_action():
    name = pick_goal_name()
    amount = read_amount("Сумма пополнения: ")
    goal, messages = gs.deposit_to_goal(name, amount)
    for message in messages:
        print(message)
    print(f"Новый баланс: {goal.current_balance:.0f}. Прогресс: {goal.get_progress():.1f}%.")


def withdraw_action():
    name = pick_goal_name()
    amount = read_amount("Сумма снятия: ")
    goal = gs.withdraw_from_goal(name, amount)
    print(f"Новый баланс: {goal.current_balance:.0f}. Прогресс: {goal.get_progress():.1f}%.")


def change_status_action():
    name = pick_goal_name()
    goal = gs.find_goal(name)
    print("Доступные статусы:")
    for index, status in enumerate(STATUSES, start=1):
        mark = " <- текущий" if status == goal.status else ""
        print(f"  {index}. {status}{mark}")
    choice = read_int("Новый статус (номер): ", 1, len(STATUSES))
    gs.change_goal_status(name, STATUSES[choice - 1])
    print(f"Статус цели «{goal.name}»: {goal.status}.")


def delete_goal_action():
    name = pick_goal_name()
    confirm = input(f"Удалить цель «{name}»? (д/Н): ").strip().lower()
    if confirm not in {"д", "да", "y", "yes"}:
        print("Удаление отменено.")
        return
    gs.delete_goal(name)
    print(f"Цель «{name}» удалена.")


def filter_by_category_action():
    category = read_text("Категория для фильтра: ")
    print_goals(gs.get_goals_by_category(category))


def reminders_action():
    messages = gs.get_reminders()
    if not messages:
        print("Срочных напоминаний нет.")
        return
    for message in messages:
        print(f"  • {message}")


def forecast_action():
    name = pick_goal_name()
    goal = gs.find_goal(name)
    suggested, text = goal.suggest_completion_date()
    print(text)
    if suggested and goal.deadline:
        if suggested <= goal.deadline:
            print(f"Прогноз укладывается в срок {format_date(goal.deadline)}.")
        else:
            print(
                f"Прогноз позже срока {format_date(goal.deadline)}. "
                "Стоит пополнять чаще или крупнее."
            )


def change_deadline_action():
    name = pick_goal_name()
    goal = gs.find_goal(name)
    print(f"Текущий срок: {format_date(goal.deadline)}")
    print("Если нажать Enter, не вводя дату, срок завершения будет убран.")
    deadline = read_optional_date("Новый срок (ДД.ММ.ГГГГ): ")
    gs.set_goal_deadline(name, deadline)
    print(f"Срок цели «{goal.name}»: {format_date(goal.deadline)}.")


def main():
    print("Добро пожаловать в Копилку!")
    if gs.goals:
        print(f"Загружено целей: {len(gs.goals)}.")
    else:
        print("Пока нет сохранённых целей.")

    startup_reminders = gs.get_reminders()
    if startup_reminders:
        print("\nНапоминания:")
        for message in startup_reminders:
            print(f"  • {message}")

    actions = {
        "1": add_goal_action,
        "2": list_goals_action,
        "3": show_progress_action,
        "4": deposit_action,
        "5": withdraw_action,
        "6": change_status_action,
        "7": delete_goal_action,
        "8": gs.show_overall_progress,
        "9": filter_by_category_action,
        "10": reminders_action,
        "11": forecast_action,
        "12": change_deadline_action,
    }

    while True:
        print(MENU)
        choice = input("Выберите пункт меню: ").strip()
        if choice == "0":
            print("Данные сохранены. До встречи!")
            return
        action = actions.get(choice)
        if action is None:
            print("Нет такого пункта. Введите число из меню.")
            continue
        try:
            action()
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except KeyboardInterrupt:
            print("\nОперация отменена.")


if __name__ == "__main__":
    main()
