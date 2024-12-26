import json
import logging
import os
import re
from datetime import datetime
from math import ceil
from typing import Any, Dict, List
from unicodedata import category

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


def analyze_cashback_categories(transactions: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
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


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает накопления в 'Инвесткопилке' за указанный месяц.

    Args:
        month (str): Месяц для расчета в формате 'YYYY-MM'.
        transactions (List[Dict[str, Any]]): Список транзакций.
        limit (int): Предел округления.

    Returns:
        float: Сумма накоплений.
    """
    total_saved = 0.0

    for tx in transactions:
        operation_date = tx.get("Дата операции", "")
        amount = tx.get("Сумма операции")

        # Проверка соответствия месяца
        if not operation_date.startswith(month):
            services_logger.debug(f"Пропущена транзакция с датой {operation_date}: не совпадает месяц.")
            continue

        # Проверка наличия суммы операции
        if amount is None or amount == "":
            services_logger.debug(f"Пропущена транзакция с датой {operation_date}: отсутствует сумма операции.")
            continue

        # Попытка преобразования суммы операции в float
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            services_logger.debug(
                f"Пропущена транзакция с датой {operation_date}: некорректный формат суммы {amount}."
            )
            continue

        # Расчет накоплений
        rounded_amount = (amount // limit + 1) * limit
        saved = rounded_amount - amount
        services_logger.debug(
            f"Транзакция с датой {operation_date}: сумма {amount}, округлено до {rounded_amount}, отложено {saved}."
        )
        total_saved += saved

    services_logger.info(f"Итоговая накопленная сумма: {total_saved}")
    return round(total_saved, 2)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """
    Выполняет простой поиск по заданному запросу в транзакциях.
    Args:
        transactions(List[Dict[str, Any]]): Список транзакций.
        query(str): Запрос для поиска.
    Returns:
        str: JSON-строка с транзакциями, содержащими запрос.
    """
    services_logger.info(f"Запуск простого поиска транзакций по запросу: '{query}'")
    query_lower = query.lower()
    matched_transactions = []

    for tx in transactions:
        description = tx.get("Описание операции", "").lower()
        comment = tx.get("Комментарий", "").lower()
        category = tx.get("Категория", "").lower()
        tx_type = tx.get("Тип", "").lower()

        if query_lower in description or query_lower in comment or query_lower in category or query_lower in tx_type:
            matched_transactions.append(tx)

    services_logger.info(f"Поиск завершен. Найдено {len(matched_transactions)} транзакций, соответсвующих запросу.")

    # Конвертация результата в JSON
    try:
        result_json = json.dumps(matched_transactions, ensure_ascii=False, indent=4)
        return result_json
    except TypeError as e:
        services_logger.error(f"Ошибка при конвертации результатов поиска в JSON: {e}")
        return "[]"


def filter_personal_transfers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции, относящиеся к переводам физическим лицам.
    Args:
        transactions (List[Dict[str, Any]]): Список транзакций.
    Returns:
        List[Dict[str, Any]]: Список транзакций, относящихся к переводам физическим лицам.
    """
    services_logger.info("Начало фильтрации переводов физическим лицам.")

    filtered_transactions = []

    for transaction in transactions:
        category = transaction.get("Категория", "")
        transaction_type = transaction.get("Тип", "")
        description = transaction.get("Описание операции", "")
        comment = transaction.get("Комментарий", "")

        # Проверяем основное условие на категорию и тип
        if category == "Финансовые операции" and transaction_type == "Списание":
            # Проверяем формат имени в описании
            if re.match(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$", description) and not comment:
                filtered_transactions.append(transaction)
                services_logger.debug(f"Транзакция добавлена: {transaction}")

    services_logger.info(f"Фильтрация завершена. Найдено {len(filtered_transactions)} транзакций.")
    return filtered_transactions
