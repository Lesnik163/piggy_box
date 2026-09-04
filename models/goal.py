from models.constants import STATUSES 

class Goal:
    def __init__(self, name, target_amount, category, status="активна"):
        name = name.strip()
        if not name:
            raise ValueError("Название не может быть пустым")
        self.name = name.capitalize()
        self.target_amount = target_amount
        self.current_balance = 0

        category = category.strip()
        if not category:
            raise ValueError("Категория не может быть пустой")
        self.category = category

        status = status.strip()
        if status not in STATUSES:
            raise ValueError(f"Недопустимый статус: {status}. Допустимые статусы: {STATUSES}")
        self.status = status

    def set_status(self, new_status):
        new_status = new_status.strip()
        if new_status not in STATUSES:
            raise ValueError(
                f"Недопустимый статус: {new_status}. Допустимые статусы: {STATUSES}"
            )
        if new_status == self.status:
            return

        if new_status == "выполнена" and self.current_balance < self.target_amount:
            raise ValueError(
                "Нельзя отметить выполненной: баланс меньше итоговой суммы."
            )

        if new_status == "активна" and self.current_balance >= self.target_amount:
            raise ValueError(
                "Цель уже накоплена. Статус может быть только «выполнена»."
            )

        self.status = new_status

    def __str__(self):
        return (
            f"{self.name}: {self.current_balance:.0f} из {self.target_amount:.0f} "
            f"({self.get_progress():.1f}%) — {self.status}"
        )
    def get_progress(self):
        if self.target_amount == 0:
            return 0
        return self.current_balance / self.target_amount * 100

    def get_remaining(self):
        return max(0, self.target_amount - self.current_balance)

    def show_progress(self):
        print(f"Цель: {self.name}")
        print(f"Категория: {self.category}")
        print(
            f"Накоплено: {self.current_balance:.0f} из {self.target_amount:.0f}"
        )
        print(f"Прогресс: {self.get_progress():.1f}%")
        print(f"Осталось: {self.get_remaining():.0f}")
        print(f"Статус: {self.status}")

    def increase_balance(self, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")

        remaining_amount = self.target_amount - self.current_balance

        if remaining_amount <= 0:
            raise ValueError("Цель уже достигнута, пополнение невозможно.")

        if amount > remaining_amount:
            raise ValueError(
                f"Сумма превышает оставшуюся сумму. Максимальная сумма: {remaining_amount:.0f}"
            )

        self.current_balance += amount

        if self.current_balance >= self.target_amount:
            self.set_status("выполнена")

    def decrease_balance(self, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")

        if self.current_balance < amount:
            raise ValueError(
                f"Текущий баланс меньше суммы для вычета. Текущий баланс: {self.current_balance:.0f}"
            )

        self.current_balance -= amount

        if self.current_balance < self.target_amount and self.status == "выполнена":
            self.set_status("активна")
