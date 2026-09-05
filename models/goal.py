from models.constants import MILESTONES, STATUSES
from utils.date_utils import (
    date_after_days,
    days_covered,
    days_until,
    format_date,
    from_iso,
    now_stamp,
    to_iso,
)


class Goal:
    def __init__(self, name, target_amount, category, status="активна", deadline=None):
        name = name.strip()
        if not name:
            raise ValueError("Название не может быть пустым")
        self.name = name

        try:
            target_amount = float(target_amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("Итоговая сумма должна быть числом.") from exc
        if target_amount <= 0:
            raise ValueError("Итоговая сумма должна быть больше нуля.")
        self.target_amount = target_amount

        self.current_balance = 0
        self.last_notified_percent = 0
        # История пополнений: нужна для прогноза даты завершения
        self.history = []

        category = category.strip()
        if not category:
            raise ValueError("Категория не может быть пустой")
        self.category = category

        status = status.strip()
        if status not in STATUSES:
            raise ValueError(f"Недопустимый статус: {status}. Допустимые статусы: {STATUSES}")
        self.status = status

        self.deadline = deadline

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

        if new_status != "выполнена" and self.current_balance >= self.target_amount:
            raise ValueError(
                "Цель уже накоплена. Статус может быть только «выполнена»."
            )

        self.status = new_status

    def to_dict(self):
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_balance": self.current_balance,
            "category": self.category,
            "status": self.status,
            "deadline": to_iso(self.deadline),
            "history": self.history,
            "last_notified_percent": self.last_notified_percent,
        }

    @classmethod
    def from_dict(cls, data):
        goal = cls(
            data["name"],
            data["target_amount"],
            data["category"],
            data["status"],
            from_iso(data.get("deadline")),
        )
        goal.current_balance = data["current_balance"]
        goal.last_notified_percent = data.get("last_notified_percent", 0)
        goal.history = data.get("history", [])
        return goal

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
        print(f"Накоплено: {self.current_balance:.0f} из {self.target_amount:.0f}")
        print(f"Прогресс: {self.get_progress():.1f}%")
        print(f"Осталось: {self.get_remaining():.0f}")
        print(f"Статус: {self.status}")
        print(f"Срок: {format_date(self.deadline)}")

        reminder = self.reminder()
        if reminder:
            print(reminder)

    def increase_balance(self, amount):
        amount = self._check_amount(amount)

        remaining_amount = self.target_amount - self.current_balance

        if remaining_amount <= 0:
            raise ValueError("Цель уже достигнута, пополнение невозможно.")

        if amount > remaining_amount:
            raise ValueError(
                f"Сумма превышает оставшуюся сумму. Максимальная сумма: {remaining_amount:.0f}"
            )

        self.current_balance += amount
        self.history.append({"date": now_stamp(), "amount": amount})

        if self.current_balance >= self.target_amount:
            self.set_status("выполнена")

        return self.check_milestone()

    def decrease_balance(self, amount):
        amount = self._check_amount(amount)

        if self.current_balance < amount:
            raise ValueError(
                f"Текущий баланс меньше суммы для вычета. Текущий баланс: {self.current_balance:.0f}"
            )

        self.current_balance -= amount

        if self.current_balance < self.target_amount and self.status == "выполнена":
            self.set_status("активна")

    def check_milestone(self):
        messages = []
        percent = self.get_progress()
        for milestone in MILESTONES:
            if percent >= milestone and self.last_notified_percent < milestone:
                messages.append(
                    f"Уведомление: цель «{self.name}» достигла {milestone}% "
                    f"({self.current_balance:.0f} из {self.target_amount:.0f})."
                )
                self.last_notified_percent = milestone
        return messages

    def days_until_deadline(self):
        """Сколько дней осталось до срока. Отрицательное число — просрочка."""
        return days_until(self.deadline)

    def reminder(self):
        """Текст напоминания или None, если напоминать не о чем."""
        if self.deadline is None or self.status == "выполнена":
            return None

        days = self.days_until_deadline()

        if days < 0:
            return (
                f"Просрочена цель «{self.name}»: срок был {format_date(self.deadline)} "
                f"({abs(days)} дн. назад), накоплено {self.get_progress():.1f}%."
            )
        if days == 0:
            return (
                f"Сегодня последний день цели «{self.name}». "
                f"Накоплено {self.get_progress():.1f}%."
            )
        if days <= 7:
            return (
                f"До срока цели «{self.name}» осталось {days} дн. "
                f"({format_date(self.deadline)}), накоплено {self.get_progress():.1f}%."
            )
        return None

    def suggest_completion_date(self):
        """Прогноз даты завершения по частоте и суммам прошлых пополнений."""
        if self.get_remaining() <= 0:
            return None, "Цель уже достигнута."
        if not self.history:
            return None, "Пополнений ещё не было — прогноз строить не из чего."

        days_passed = days_covered(self.history[0]["date"], self.history[-1]["date"])

        total = sum(item["amount"] for item in self.history)
        per_day = total / days_passed
        if per_day <= 0:
            return None, "Темп пополнений слишком мал для прогноза."

        days_left = int(self.get_remaining() / per_day) + 1
        suggested = date_after_days(days_left)

        average = total / len(self.history)
        every = days_passed / len(self.history)
        text = (
            f"Пополнений: {len(self.history)}, средний взнос {average:.0f} "
            f"примерно раз в {every:.1f} дн.\n"
            f"Темп: {per_day:.0f} в день, осталось накопить {self.get_remaining():.0f}.\n"
            f"Ожидаемая дата завершения: {format_date(suggested)} (через {days_left} дн.)."
        )
        return suggested, text

    def _check_amount(self, amount):
        """Общая проверка суммы для пополнения и снятия."""
        try:
            amount = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("Сумма должна быть числом.") from exc
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")
        return amount
