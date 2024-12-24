import os
import json
import pytest
import pandas as pd
from src.views import main_page, events_page


@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "transactions.json"
    yield file_path


def test_main_page_valid_data(temp_file):
    transactions = [
        {"Сумма": "1500", "Тип": "Списание", "Кэшбек": "+15"},
        {"Сумма": "2000", "Тип": "Пополнение", "Кэшбек": "+20"},
        {"Сумма": "300", "Тип": "Списание", "Кэшбек": "+5"},
    ]
    temp_file.write_text(json.dumps(transactions, ensure_ascii=False), encoding="utf-8")
    result = main_page(str(temp_file))
    result_data = json.loads(result)
    assert result_data["total_transactions"] == 3
    assert len(result_data["transactions"]) == 3


def test_main_page_file_not_found(temp_file):
    if temp_file.exists():
        os.remove(temp_file)
    result = main_page(str(temp_file))
    result_data = json.loads(result)
    assert "error" in result_data
    assert "не найден" in result_data["error"]


def test_main_page_empty_data(temp_file):
    temp_file.write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")
    result = main_page(str(temp_file))
    result_data = json.loads(result)
    assert result_data["total_transactions"] == 0
    assert result_data["transactions"] == []


def test_events_page_valid_data():
    data = pd.DataFrame([
        {"Категория": "Еда", "Сумма": 150},
        {"Категория": "Еда", "Сумма": 200},
        {"Категория": "Развлечения", "Сумма": 300},
    ])
    result = events_page(data)
    result_data = json.loads(result)
    assert result_data["total_events"] == 3
    assert result_data["categories"] == {"Еда": 2, "Развлечения": 1}


def test_events_page_empty_dataframe():
    df = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма", "Тип"])
    result = events_page(df)
    result_data = json.loads(result)
    assert result_data["total_events"] == 0
    assert result_data["categories"] == {}


def test_events_page_missing_columns():
    df = pd.DataFrame({"Дата операции": ["2024-12-01"], "Сумма": [500]})
    with pytest.raises(KeyError, match="Отсутствуют обязательные колонки"):
        events_page(df)


def test_events_page_invalid_data_format():
    data = {
        "Категория": ["Продукты", "Транспорт", "Развлечения"],
        "Сумма": ["500", "1000", "invalid_sum"],
    }
    df = pd.DataFrame(data)
    result = events_page(df)
    result_data = json.loads(result)

    # Проверяем, что только валидные данные учтены
    assert result_data["total_events"] == 2
    assert result_data["categories"] == {"Продукты": 1, "Транспорт": 1}

