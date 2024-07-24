import pytest
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

# Предположим, что ваша функция находится в файле `your_module.py`
from src.utils import from_xlsx, list_to_df, investment_dict, convert_date_format, ROOT_PATH, path_xlsx


# Создаем фиктивные данные для теста
@pytest.fixture
def mock_excel_data():
    data = {
        "Column1": [1, 2, 3],
        "Column2": ["a", "b", "c"]
    }
    return pd.DataFrame(data)


@patch('src.utils.pd.read_excel')
@patch('src.utils.Path')
def test_from_xlsx(mock_path, mock_read_excel, mock_excel_data):
    # Настройка mock-объектов
    mock_read_excel.return_value = mock_excel_data
    mock_path.return_value = Path(ROOT_PATH, path_xlsx)

    # Ожидаемый результат
    expected_result = [
        {"Column1": 1, "Column2": "a"},
        {"Column1": 2, "Column2": "b"},
        {"Column1": 3, "Column2": "c"}
    ]

    # Вызов функции
    result = from_xlsx()

    # Проверка результата
    assert result == expected_result

    # Проверка вызовов mock-объектов
    mock_read_excel.assert_called_once_with(Path(ROOT_PATH, path_xlsx))


def test_list_to_df():
    # Тестовые данные
    input_data = [
        {"Column1": 1, "Column2": "a"},
        {"Column1": 2, "Column2": "b"},
        {"Column1": 3, "Column2": "c"}
    ]

    # Ожидаемый результат
    expected_data = pd.DataFrame(input_data)

    # Вызов функции
    result = list_to_df(input_data)

    # Проверка результата
    pd.testing.assert_frame_equal(result, expected_data)


def test_list_to_df_empty():
    # Тестовые данные: пустой список
    input_data = []

    # Ожидаемый результат: пустой DataFrame
    expected_data = pd.DataFrame(input_data)

    # Вызов функции
    result = list_to_df(input_data)

    # Проверка результата
    pd.testing.assert_frame_equal(result, expected_data)


def test_list_to_df_missing_columns():
    # Тестовые данные с отсутствующими столбцами в одном из словарей
    input_data = [
        {"Column1": 1, "Column2": "a"},
        {"Column1": 2},
        {"Column1": 3, "Column2": "c"}
    ]

    # Ожидаемый результат
    expected_data = pd.DataFrame(input_data)

    # Вызов функции
    result = list_to_df(input_data)

    # Проверка результата
    pd.testing.assert_frame_equal(result, expected_data)


def test_investment_dict():
    # Тестовые данные
    input_data = [
        {"Дата операции": "2022-01-01", "Сумма операции": 100, "Другой ключ": "значение"},
        {"Дата операции": "2022-02-02", "Сумма операции": 200},
        {"Дата операции": "2022-03-03", "Сумма операции": 150, "Еще один ключ": "другое значение"}
    ]

    # Ожидаемый результат
    expected_data = [
        {"Дата операции": "2022-01-01", "Сумма операции": 100},
        {"Дата операции": "2022-02-02", "Сумма операции": 200},
        {"Дата операции": "2022-03-03", "Сумма операции": 150}
    ]

    # Вызов функции
    result = investment_dict(input_data)

    # Проверка результата
    assert result == expected_data


def test_investment_dict_missing_keys():
    # Тестовые данные с отсутствующими ключами
    input_data = [
        {"Сумма операции": 100, "Другой ключ": "значение"},
        {"Дата операции": "2022-02-02"},
        {"Дата операции": "2022-03-03", "Сумма операции": 150}
    ]

    # Ожидаемый результат
    expected_data = [
        {"Сумма операции": 100},
        {"Дата операции": "2022-02-02"},
        {"Дата операции": "2022-03-03", "Сумма операции": 150}
    ]

    # Вызов функции
    result = investment_dict(input_data)

    # Проверка результата
    assert result == expected_data


def test_investment_dict_empty():
    # Тестовые данные: пустой список
    input_data = []

    # Ожидаемый результат: пустой список
    expected_data = []

    # Вызов функции
    result = investment_dict(input_data)

    # Проверка результата
    assert result == expected_data


def test_investment_dict_all_keys_missing():
    # Тестовые данные, где отсутствуют все нужные ключи
    input_data = [
        {"Другой ключ": "значение"},
        {"Еще один ключ": "другое значение"}
    ]

    # Ожидаемый результат: пустые словари
    expected_data = [
        {},
        {}
    ]

    # Вызов функции
    result = investment_dict(input_data)

    # Проверка результата
    assert result == expected_data


@pytest.mark.parametrize("date", ["01.01.2022 12:00:00", "21.23.2023 06:50:00", "05.10.2020 19:09:50"])
def test_convert_date_format_valid(date):
    # Тестовые данные
    input_date = "01.01.2022 12:00:00"

    # Ожидаемый результат
    expected_date = "2022-01-01"

    # Вызов функции
    result = convert_date_format(input_date)

    # Проверка результата
    assert result == expected_date


def test_convert_date_format_invalid_format():
    # Тестовые данные с неправильным форматом
    input_date = "01-01-2022 12:00:00"

    # Проверка, что вызывается исключение ValueError
    with pytest.raises(ValueError):
        convert_date_format(input_date)


def test_convert_date_format_different_time():
    # Тестовые данные с другим временем
    input_date = "15.03.2023 23:59:59"

    # Ожидаемый результат
    expected_date = "2023-03-15"

    # Вызов функции
    result = convert_date_format(input_date)

    # Проверка результата
    assert result == expected_date


def test_convert_date_format_no_time():
    # Тестовые данные с отсутствующим временем
    input_date = "01.01.2022"

    # Проверка, что вызывается исключение ValueError
    with pytest.raises(ValueError):
        convert_date_format(input_date)


def test_convert_date_format_empty_string():
    # Тестовые данные: пустая строка
    input_date = ""

    # Проверка, что вызывается исключение ValueError
    with pytest.raises(ValueError):
        convert_date_format(input_date)
