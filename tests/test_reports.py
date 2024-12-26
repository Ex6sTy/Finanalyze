import json

import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category_valid_data():
    data = pd.DataFrame(
        {
            "Дата операции": ["2024-01-01", "2024-01-15", "2024-02-20"],
            "Категория": ["Еда", "Еда", "Транспорт"],
            "Сумма": [100, 200, 300],
        }
    )
    result = spending_by_category(data, "Еда", "2024-01-01")
    result_data = json.loads(result)

    assert result_data["category"] == "Еда"
    assert result_data["total_spent"] == 300
    assert len(result_data["transactions"]) == 2


def test_spending_by_category_no_matching_category():
    data = pd.DataFrame(
        {
            "Дата операции": ["2024-01-01", "2024-01-15", "2024-02-20"],
            "Категория": ["Транспорт", "Развлечения", "Продукты"],
            "Сумма": [100, 200, 300],
        }
    )
    result = spending_by_category(data, "Еда", "2024-01-01")
    result_data = json.loads(result)

    assert result_data["category"] == "Еда"
    assert result_data["total_spent"] == 0
    assert result_data["transactions"] == []


def test_spending_by_category_missing_columns():
    data = pd.DataFrame({"Дата операции": ["2024--01-01", "2024-01-15"], "Сумма": [100, 200]})
    result = spending_by_category(data, "Еда", "2024-01-01")
    result_data = json.loads(result)

    assert "error" in result_data
    assert "Отсутствуют необходимые колонки" in result_data["error"]


def test_spending_by_category_invalid_date_format():
    data = pd.DataFrame(
        {
            "Дата операции": ["invalid_date", "2024-01-15", "2024-02-20"],
            "Категория": ["Еда", "Еда", "Транспорт"],
            "Сумма": [100, 200, 300],
        }
    )
    result = spending_by_category(data, "Еда", "2024-01-01")
    result_data = json.loads(result)

    assert "error" in result_data
    assert "Ошибка преобразования дат" in result_data["error"]


def test_spending_by_category_empty_dataframe():
    data = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма"])
    result = spending_by_category(data, "Еда", "2024-01-01")
    result_data = json.loads(result)

    assert result_data["category"] == "Еда"
    assert result_data["total_spent"] == 0
    assert result_data["transactions"] == []
