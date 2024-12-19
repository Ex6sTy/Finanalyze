import pytest
import json
from src.services import analyze_cashback_categories, investment_bank, simple_search, filter_personal_transfers

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

def test_investment_bank_valid_data():
    transactions = [
        {"Дата операции": "2024-12-01", "Сумма операции": "174.5"},
        {"Дата операции": "2024-12-15", "Сумма операции": "49.99"},
        {"Дата операции": "2024-12-20", "Сумма операции": "333.33"},
        {"Дата операции": "2024-11-01", "Сумма операции": "200.00"}, # Другой месяц
    ]
    result = investment_bank("2024-12", transactions, 100)
    assert result == pytest.approx(142.18, 0.01)

def rest_investment_bank_invalid_limit():
    transactions = [
        {"Дата операции": "2024-12-01", "Сумма операции": "174.25"},
    ]
    with pytest.raises(ValueError, match="Предел округления должен быть равен 10, 50 или 100 ₽."):
        investment_bank("2024-12", transactions, 50)

def test_investment_bank_empty_transactions():
    transactions = []
    result = investment_bank("2024-12", transactions, 50)
    assert result == 0.0

def test_investment_bank_invalid_date_format():
    transactions = [
        {"Дата операции": "12-01-2024", "Сумма операции": "100.00"}, # Неверный формат даты
    ]
    result = investment_bank("2024-12", transactions, 50)
    assert result == 0.0

def test_investment_bank_missing_amount_field():
    transactions = [
        {"Дата операции": "2024-12-01"},
    ]
    result = investment_bank("2024-12", transactions, 50.0)
    assert result == 0.0

def test_investment_bank_partial_matching_data():
    transactions = [
        {"Дата операции": "2024-12-01", "Сумма операции": "174.5"},
        {"Дата операции": "2024-12-15", "Сумма операции": "49.99"},
        {"Дата операции": "2024-12-20", "Сумма операции": "333.33"},
        {"Дата операции": "2024-11-01", "Сумма операции": "200.00"},
    ]
    result = investment_bank("2024-12", transactions, 100)
    assert result == pytest.approx(142.18, 0.01)

def test_simple_search_full_match():
    transactions = [
        {"Описание операции": "MOSKVA\OZON RU", "Категория": "Маркетплейсы", "Тип": "Списание", "Комментарий": ""},
        {"Описание операции": "Вход. перевод от клиента Альфа-Банка", "Категория": "Пополнения", "Тип": "Пополнение	", "Комментарий": "Возврат средств по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреевич. Без НДС по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреев"},
    ]
    result = simple_search(transactions, "маркетплейсы")
    result_data = json.loads(result)
    assert len(result_data) == 1
    assert result_data[0]["Категория"] == "Маркетплейсы"

def test_simple_search_partial_match():
        transactions = [
            {"Описание операции": "MOSKVA\OZON RU",
             "Категория": "Маркетплейсы",
             "Тип": "Списание",
             "Комментарий": ""},
            {"Описание операции": "Вход. перевод от клиента Альфа-Банка",
             "Категория": "Пополнения",
             "Тип": "Пополнение	",
             "Комментарий": "Возврат средств по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреевич. Без НДС по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреев"},
        ]
        result = simple_search(transactions, "пополн")
        result_data = json.loads(result)
        assert len(result_data) == 1
        assert result_data[0]["Категория"] == "Пополнения"

def test_simple_search_no_match():
    transactions = [
            {"Описание операции": "MOSKVA\OZON RU",
             "Категория": "Маркетплейсы",
             "Тип": "Списание", "Комментарий": ""},
            {"Описание операции": "Вход. перевод от клиента Альфа-Банка",
             "Категория": "Пополнения",
             "Тип": "Пополнение	",
             "Комментарий": "Возврат средств по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреевич. Без НДС по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреев"},
        ]
    result = simple_search(transactions, "такси")
    result_data = json.loads(result)
    assert len(result_data) == 0

def test_simple_search_empty_transactions():
    transactions = []
    result = simple_search(transactions, "продукты")
    result_data = json.loads(result)
    assert len(result_data) == 0

def test_simple_search_empty_query():
    transactions = [
        {"Описание операции": "MOSKVA\OZON RU",
         "Категория": "Маркетплейсы",
         "Тип": "Списание", "Комментарий": ""},
        {"Описание операции": "Вход. перевод от клиента Альфа-Банка",
         "Категория": "Пополнения",
         "Тип": "Пополнение	",
         "Комментарий": "Возврат средств по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреевич. Без НДС по дог. N 3530772 от 07.04.2023. Богатов Артемий Андреев"},
    ]
    result = simple_search(transactions, "")
    result_data = json.loads(result)
    assert len(result_data) == 2


def test_filter_personal_transfers_valid_data():
    transactions = [
        {"Описание операции": "Иван М.", "Комментарий": "", "Тип": "Списание", "Категория": "Финансовые операции"},
        {"Описание операции": "Анастасия О.", "Комментарий": "Перевод денежных средств", "Тип": "Списание",
         "Категория": "Финансовые операции"},
        {"Описание операции": "Руслан К.", "Комментарий": "", "Тип": "Списание", "Категория": "Финансовые операции"},
        {"Описание операции": "Александр К.", "Комментарий": "", "Тип": "Пополнение", "Категория": "Финансовые операции"},
    ]
    result = filter_personal_transfers(transactions)
    expected = [
        {"Описание операции": "Иван М.", "Комментарий": "", "Тип": "Списание", "Категория": "Финансовые операции"},
        {"Описание операции": "Руслан К.", "Комментарий": "", "Тип": "Списание", "Категория": "Финансовые операции"},
    ]
    print("Результат фильтрации:", result)
    print("Ожидаемый результат:", expected)
    assert sorted(result, key=lambda x: (x["Описание операции"], x["Комментарий"])) == \
           sorted(expected, key=lambda x: (x["Описание операции"], x["Комментарий"]))



def test_filter_personal_transfers_empty_data():
    transactions = []
    result = filter_personal_transfers(transactions)
    assert result == []


def test_filter_personal_transfers_no_valid_type():
    transactions = [
        {"Описание операции": "Иван М.", "Комментарий": "", "Тип": "Пополнение", "Категория": "Финансовые операции"},
        {"Описание операции": "Руслан К.", "Комментарий": "Перевод денежных средств", "Тип": "Пополнение",
         "Категория": "Финансовые операции"},
    ]
    result = filter_personal_transfers(transactions)
    assert result == []












