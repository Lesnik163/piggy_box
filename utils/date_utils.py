"""Работа с датами: разбор, вывод и подсчёт дней."""

from datetime import date, datetime, timedelta

# Формат даты для пользователя: 31.12.2026
DATE_FORMAT = "%d.%m.%Y"
# Формат отметки времени в истории пополнений: 31.12.2026 18:45
DATETIME_FORMAT = "%d.%m.%Y %H:%M"


def parse_date(value):
    """Строка «31.12.2026» -> объект date. При плохом вводе — понятная ошибка."""
    try:
        return datetime.strptime(value.strip(), DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(
            "Дата должна быть в формате ДД.ММ.ГГГГ, например 31.12.2026."
        ) from exc


def format_date(value):
    """Объект date -> строка для показа пользователю."""
    if value is None:
        return "не задан"
    return value.strftime(DATE_FORMAT)


def to_iso(value):
    """date -> строка для JSON («2026-12-31») или None, если срока нет."""
    if value is None:
        return None
    return value.isoformat()


def from_iso(value):
    """Строка из JSON -> объект date или None, если срока нет."""
    if not value:
        return None
    return date.fromisoformat(value)


def now_stamp():
    """Текущий момент строкой — для записи в историю пополнений."""
    return datetime.now().strftime(DATETIME_FORMAT)


def days_until(target):
    """Сколько дней от сегодня до target. Отрицательное число — дата в прошлом."""
    if target is None:
        return None
    return (target - date.today()).days


def date_after_days(days):
    """Какая дата будет через days дней от сегодня."""
    return date.today() + timedelta(days=days)


def is_past(value):
    """Дата уже прошла?"""
    return value is not None and value < date.today()


def days_covered(first_stamp, last_stamp):
    """Сколько дней охватывают две отметки истории.

    Минимум 1: если все пополнения были в один день, делим на 1, а не на 0.
    """
    first = datetime.strptime(first_stamp, DATETIME_FORMAT)
    last = datetime.strptime(last_stamp, DATETIME_FORMAT)
    return max(1, (last.date() - first.date()).days + 1)
