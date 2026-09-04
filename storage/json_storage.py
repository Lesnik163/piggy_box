import json
from pathlib import Path

from models.goal import Goal

DATA_FILE = Path("data/goals.json")


def save_goals(goals):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump([goal.to_dict() for goal in goals], file, ensure_ascii=False, indent=4)


def load_goals():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    return [Goal.from_dict(goal) for goal in data]
