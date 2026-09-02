class Goal:
  def __init__(self, name, target_amount, status, category):
    self.name = name
    self.target_amount = target_amount
    self.current_balance = 0
    self.status = status
    self.category = category

  def __str__(self):
    percent = self.current_balance / self.target_amount * 100
    return (
        f"{self.name}: {self.current_balance:.0f} из {self.target_amount:.0f} "
        f"({percent:.1f}%) — {self.status}"
    )
    
goals = []

def add_goal(name, target_amount, status, category):
  goal = Goal(name, target_amount, status, category)
  goals.append(goal)
  print(f"Цель {goal} добавлена")
  return goal

