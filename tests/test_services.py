import pytest


from src.services import analyze_cashback_categories

def test_analyze_cashback_categories_valid_data():
    transactions = [
        {"Дата операции": "15.12.2024", "Категория": "Техника", "Кэшбек": "+74.5"},
        {"Дата операции": "18.12.2024", "Категория": "Фастфуд", "Кэшбек": "+30"},
        {"Дата операции": "17.12.2024", "Категория": "Фастфуд", "Кэшбек": "+395"},
        {"Дата операции": "25.11.2024", "Категория": "Продукты", "Кэшбек": "+23.5"},
        {"Дата операции": "15.11.2024", "Категория": "Кафе и рестораны", "Кэшбек": "+40"},
    ]
    result = analyze_cashback_categories(transactions, 2024, 12)
    assert result == {"Техника": 74.5, "Фастфуд": 425}


def test_analyze_cashback_categories_no_cashback():
    transactions = [
        {"Дата операции": "15.12.2024", "Категория": "Техника", "Кэшбек": "+0"},
        {"Дата операции": "18.12.2024", "Категория": "Фастфуд", "Кэшбек": "None"},
        {"Дата операции": "17.12.2024", "Категория": "Фастфуд"},
        {"Дата операции": "25.11.2024", "Категория": "Продукты", "Кэшбек": ""},
        {"Дата операции": "20.12.2024", "Категория": "Продукты", "Кэшбек": None},
    ]
    result = analyze_cashback_categories(transactions, 2024, 12)
    assert result == {"Продукты": 0.0, "Техника": 0.0, "Фастфуд": 0.0}



def test_analyze_cashback_categories_no_matching_transactions():
    transactions = [
        {"Дата операции": "15.12.2024", "Категория": "Техника", "Кэшбек": "+150"},
        {"Дата операции": "18.12.2024", "Категория": "Фастфуд", "Кэшбек": "+50"},
    ]
    result = analyze_cashback_categories(transactions, 2023, 12)
    assert result == {}


def test_analyze_cashback_categories_invalid_cashback_format():
    transactions = [
        {"Дата операции": "15.12.2024", "Категория": "Техника", "Кэшбек": "150 рублей"},
        {"Дата операции": "18.12.2024", "Категория": "Фастфуд", "Кэшбек": "+50"},
        {"Дата операции": "20.12.2024", "Категория": "Техника", "Кэшбек": "+15.5$"},
    ]
    result = analyze_cashback_categories(transactions, 2024, 12)
    assert result == {"Техника": 0.0, "Фастфуд": 50.0}

def test_analyze_cashback_categories_empty_transactions():
    transactions = []
    result = analyze_cashback_categories(transactions, 2024, 12)
    assert result == {}
