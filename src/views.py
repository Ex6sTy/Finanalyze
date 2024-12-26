import json

import pandas as pd

from src.logging_config import setup_logger

# Настройка логгера для главной страницы
views_logger = setup_logger("views", "logs/views.log")

def main_page(file_path: str) -> str:
    """
    Обрабатывает файл с транзакциями и возвращает их общее количество и содержимое в формате JSON.

    Args:
        file_path (str): Путь к файлу с транзакциями.

    Returns:
        str: JSON-строка с общим количеством транзакций и их данными.
              В случае ошибки возвращается JSON с описанием ошибки.

    Raises:
        FileNotFoundError: Если файл не найден.
        UnicodeDecodeError: Если возникла ошибка кодировки при чтении файла.
    """
    views_logger.info(f"Начало обработки файла: {file_path}")
    try:
        with open(file_path, encoding="utf-8") as f:
            transactions = json.load(f)
        views_logger.info(f"Файл обработан. Найдено транзакций: {len(transactions)}")
        return json.dumps(
            {"total_transactions": len(transactions), "transactions": transactions},
            ensure_ascii=False,
            indent=4,
        )
    except FileNotFoundError:
        views_logger.error(f"Файл {file_path} не найден.")
        return json.dumps({"error": f"Файл {file_path} не найден."}, ensure_ascii=False, indent=4)
    except UnicodeDecodeError as e:
        views_logger.error(f"Ошибка кодировки файла {file_path}: {e}")
        return json.dumps(
            {"error": f"Ошибка кодировки файла {file_path}"},
            ensure_ascii=False,
            indent=4,
        )

# Настройка логгера для страницы событий
events_logger = setup_logger("events", "logs/events.log")

def events_page(data: pd.DataFrame) -> str:
    """
    Обрабатывает события из DataFrame и возвращает JSON с анализом категорий.

    Args:
        data (pd.DataFrame): DataFrame с колонками "Категория" и "Сумма".

    Returns:
        str: JSON-строка с общим количеством событий и подсчётом категорий.

    Raises:
        KeyError: Если отсутствуют обязательные колонки "Категория" или "Сумма".
    """
    events_logger.info("Начало обработки событий.")

    # Проверка наличия обязательных колонок
    required_columns = {"Категория", "Сумма"}
    if not required_columns.issubset(data.columns):
        events_logger.error(f"Отсутствуют обязательные колонки: {required_columns - set(data.columns)}")
        raise KeyError(f"Отсутствуют обязательные колонки: {required_columns - set(data.columns)}")

    # Фильтрация данных
    data["Сумма"] = pd.to_numeric(data["Сумма"], errors="coerce")  # Преобразуем "Сумма" в числовой формат
    valid_data = data.dropna(subset=["Сумма"])  # Удаляем строки с некорректной суммой

    if valid_data.empty:
        events_logger.warning("DataFrame пуст.")
        return json.dumps({"total_events": 0, "categories": {}}, ensure_ascii=False, indent=4)

    # Подсчёт категорий
    category_counts = valid_data["Категория"].value_counts().to_dict()
    total_events = valid_data.shape[0]

    events_logger.info(f"Обработано {total_events} событий.")
    return json.dumps(
        {"total_events": total_events, "categories": category_counts},
        ensure_ascii=False,
        indent=4,
    )
