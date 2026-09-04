from models.goal import Goal

goals = []

def add_goal(name, target_amount, category, status="активна"):
    goal = Goal(name, target_amount, category, status)
    goals.append(goal)
    return goal

def get_goals_by_category(category):
    category = category.strip()
    if not category:
        raise ValueError("Категория не может быть пустой")
    return [goal for goal in goals if goal.category == category]