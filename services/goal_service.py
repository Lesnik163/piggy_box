from models.goal import Goal
from storage.json_storage import load_goals, save_goals
from utils.date_utils import is_past

goals = load_goals()


def add_goal(name, target_amount, category, status="активна", deadline=None):
    if find_goal_or_none(name) is not None:
        raise ValueError(f"Цель «{name.strip()}» уже существует.")
    if is_past(deadline):
        raise ValueError("Дата завершения не может быть в прошлом.")

    goal = Goal(name, target_amount, category, status, deadline)
    goals.append(goal)
    save_goals(goals)
    return goal


def delete_goal(name):
    goal = find_goal(name)
    goals.remove(goal)
    save_goals(goals)
    return goal


def find_goal_or_none(name):
    name = name.strip().lower()
    for goal in goals:
        if goal.name.lower() == name:
            return goal
    return None


def find_goal(name):
    goal = find_goal_or_none(name)
    if goal is None:
        raise ValueError(f"Цель «{name.strip()}» не найдена")
    return goal


def get_goals_by_category(category):
    category = category.strip()
    if not category:
        raise ValueError("Категория не может быть пустой")
    return [goal for goal in goals if goal.category.lower() == category.lower()]


def get_overall_progress():
    if not goals:
        return {
            "count": 0,
            "completed": 0,
            "total_balance": 0,
            "total_target": 0,
            "percent": 0,
        }

    total_balance = sum(goal.current_balance for goal in goals)
    total_target = sum(goal.target_amount for goal in goals)
    completed = sum(1 for goal in goals if goal.status == "выполнена")
    percent = 0 if total_target == 0 else total_balance / total_target * 100

    return {
        "count": len(goals),
        "completed": completed,
        "total_balance": total_balance,
        "total_target": total_target,
        "percent": round(percent, 1),
    }


def show_overall_progress():
    stats = get_overall_progress()
    if stats["count"] == 0:
        print("Нет целей.")
        return
    print(
        f"Целей: {stats['count']}, выполнено: {stats['completed']}.\n"
        f"Накоплено {stats['total_balance']:.0f} из {stats['total_target']:.0f} "
        f"({stats['percent']}%)."
    )


def get_reminders():
    """Напоминания по срокам всех целей."""
    messages = []
    for goal in goals:
        text = goal.reminder()
        if text:
            messages.append(text)
    return messages


def deposit_to_goal(name, amount):
    goal = find_goal(name)
    messages = goal.increase_balance(amount)
    save_goals(goals)
    return goal, messages


def withdraw_from_goal(name, amount):
    goal = find_goal(name)
    goal.decrease_balance(amount)
    save_goals(goals)
    return goal


def change_goal_status(name, new_status):
    goal = find_goal(name)
    goal.set_status(new_status)
    save_goals(goals)
    return goal


def set_goal_deadline(name, deadline):
    goal = find_goal(name)
    if is_past(deadline):
        raise ValueError("Дата завершения не может быть в прошлом.")
    goal.deadline = deadline
    save_goals(goals)
    return goal
