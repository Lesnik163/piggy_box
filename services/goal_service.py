from models.goal import Goal
from storage.json_storage import load_goals, save_goals

goals = load_goals()


def add_goal(name, target_amount, category, status="активна"):
    goal = Goal(name, target_amount, category, status)
    goals.append(goal)
    save_goals(goals)
    return goal


def delete_goal(name):
    name = name.strip()
    for goal in goals:
        if goal.name.lower() == name.lower():
            goals.remove(goal)
            save_goals(goals)
            return goal
    raise ValueError(f"Цель «{name}» не найдена")


def get_goals_by_category(category):
    category = category.strip()
    if not category:
        raise ValueError("Категория не может быть пустой")
    return [goal for goal in goals if goal.category == category]