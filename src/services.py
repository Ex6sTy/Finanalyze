import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

# Создаем директорию для логов, если она отсутствует
os.makedirs("logs", exist_ok=True)

# Настройка логгера
services_logger = logging.getLogger("services")
services_logger.setLevel(logging.DEBUG)

# Настройка обработчика и форматтера
file_handler = logging.FileHandler("logs/services.log", mode="w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
services_logger.addHandler(file_handler)


import re

def analyze_cashback_categories(
    transactions: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, float]:
    """
    Анализирует транзакции и возвращает сумму кешбэка по категориям за указанный месяц.

    Args:
        transactions (List[Dict[str, Any]]): Список транзакций.
        year (int): Год для анализа.
        month (int): Месяц для анализа.

    Returns:
        Dict[str, float]: Словарь с категориями и суммой кешбэка.
    """
    services_logger.info(f"Начало анализа кешбека за {year}-{month:02d}")

    # Фильтрация транзакций по году и месяцу
    filtered_transactions = [
        tx
        for tx in transactions
        if "Дата операции" in tx
        and datetime.strptime(tx["Дата операции"], "%d.%m.%Y").year == year
        and datetime.strptime(tx["Дата операции"], "%d.%m.%Y").month == month
    ]
    services_logger.debug(f"Найдено {len(filtered_transactions)} транзакций для анализа.")

    # Подсчет кешбэка по категориям
    cashback_by_category = {}
    for tx in filtered_transactions:
        category = tx.get("Категория", "Неизвестная категория")
        cashback_raw = tx.get("Кэшбек", 0)

        # Извлечение числового значения из строки кешбэка
        if isinstance(cashback_raw, str):
            cashback_match = re.fullmatch(r"[+-]?\d*\.?\d+", cashback_raw)
            cashback = float(cashback_match.group()) if cashback_match else 0.0
        elif isinstance(cashback_raw, (int, float)):
            cashback = float(cashback_raw)
        else:
            cashback = 0.0

        cashback_by_category[category] = cashback_by_category.get(category, 0) + cashback

    services_logger.info("Анализ кэшбека завершен.")
    return cashback_by_category
