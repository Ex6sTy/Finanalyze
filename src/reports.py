import json
from datetime import datetime, timedelta
import pandas as pd
from src.logging_config import setup_logger
import logging
import numpy as np
from src.services import formatter

# Настройка логгера
reports_logger = setup_logger("reports", "logs/reports.log", level=logging.DEBUG)

def spending_by_category(df: pd.DataFrame, category: str, start_date: str) -> str:
    reports_logger.info(f"Начало анализа трат по категории '{category}' с даты {start_date}.")

    # Проверка на наличие необходимых колонок
    required_columns = {"Дата операции", "Категория", "Сумма"}
    if not required_columns.issubset(df.columns):
        error_message = f"Отсутствуют необходимые колонки: {required_columns - set(df.columns)}"
        reports_logger.error(error_message)
        return json.dumps({"error": error_message}, ensure_ascii=False, indent=4)

    # Преобразование дат
    try:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=90)  # 3 месяца
    except Exception as e:
        error_message = f"Ошибка преобразования дат: {str(e)}"
        reports_logger.error(error_message)
        return json.dumps({"error": error_message}, ensure_ascii=False, indent=4)

    # Фильтрация по категории и дате
    filtered_df = df[
        (df["Категория"] == category) &
        (df["Дата операции"] >= start_date) &
        (df["Дата операции"] < end_date)
    ]

    # Преобразование дат операций в строки
    if not filtered_df.empty:
        filtered_df["Дата операции"] = filtered_df["Дата операции"].dt.strftime("%Y-%m-%d")

    # Проверка на пустой результат
    if filtered_df.empty:
        reports_logger.warning(f"Нет транзакций по категории '{category}' за указанный период.")
        return json.dumps({"category": category, "total_spent": 0, "transactions": []}, ensure_ascii=False, indent=4)

    # Подсчет общей суммы
    total_spending = int(filtered_df["Сумма"].sum())  # Преобразуем в int для JSON совместимости

    # Формирование результата
    result = {
        "category": category,
        "total_spent": total_spending,
        "start_date": start_date.strftime("%Y-%m-%d"),  # Преобразуем дату в строку
        "end_date": end_date.strftime("%Y-%m-%d"),      # Преобразуем дату в строку
        "transactions": filtered_df.to_dict(orient="records")
    }

    reports_logger.info(f"Траты по категории '{category}': {total_spending} за период {start_date.date()} - {end_date.date()}.")
    return json.dumps(result, ensure_ascii=False, indent=4)
