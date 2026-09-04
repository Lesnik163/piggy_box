from models.goal import Goal
from storage.json_storage import load_goals, save_goals

goals = load_goals()


def add_goal(name, target_amount, category, status="активна"):
    goal = Goal(name, target_amount, category, status)
    print(f'Добавлена цель: {goal.name}')
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

def get_overall_progress():
  if not goals:
    return {
      "count": 0,
      "total": 0,
      "progress": 0,
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
    "total": total_target,
    "progress": percent,
    "total_balance": total_balance,
    "total_target": total_target,
    "percent": percent,
  }


def deposit_to_goal(name, amount):
    name = name.strip()
    for goal in goals:
        if goal.name.lower() == name.lower():
            messages = goal.increase_balance(amount)
            save_goals(goals)
            return goal, messages
    raise ValueError(f"Цель «{name}» не найдена")


def show_overall_progress():
    stats = get_overall_progress()
    if stats["count"] == 0:
        print("Нет целей.")
        return
    print(
        f"Целей: {stats['count']}, выполнено: {stats['completed']}.\n"
        f"Накоплено {stats['total_balance']:.0f} из {stats['total_target']:.0f} "
        f"({stats['percent']:.1f}%)."
    )