# piggy_box — консольное приложение «Копилка»

Управление накоплениями: цели, баланс, прогресс, категории, JSON между сессиями.

## Запуск

```bash
python main.py
```

Запускай из корня проекта (`piggy_box/`).

## Структура

- `models/goal.py` — класс цели
- `services/goal_service.py` — список целей и операции
- `storage/json_storage.py` — сохранение в `data/goals.json`
- `main.py` — консольное меню
