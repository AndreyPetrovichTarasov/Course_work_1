import pytest
from unittest.mock import patch, mock_open
from datetime import datetime
import json
import pandas as pd
import requests
import yfinance as yf

from src.views import (
    load_user_settings, get_greeting, filter_transactions, calculate_card_stats,
    get_top_transactions, get_currency_rates, get_stock_prices, generate_report
)


# Тест для функции load_user_settings
@patch("builtins.open", new_callable=mock_open,
       read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}')
def test_load_user_settings(mock_open):
    result = load_user_settings()
    expected = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
    assert result == expected


# Тест для функции get_greeting
def test_get_greeting():
    # Утро
    morning_time = datetime(2024, 7, 19, 7, 0, 0)
    assert get_greeting(morning_time) == "Доброе утро"

    # День
    afternoon_time = datetime(2024, 7, 19, 13, 0, 0)
    assert get_greeting(afternoon_time) == "Добрый день"

    # Вечер
    evening_time = datetime(2024, 7, 19, 19, 0, 0)
    assert get_greeting(evening_time) == "Добрый вечер"

    # Ночь
    night_time = datetime(2024, 7, 19, 23, 0, 0)
    assert get_greeting(night_time) == "Доброй ночи"


# Тест для функции calculate_card_stats
def test_calculate_card_stats():
    data = {
        "Номер карты": ["1234", "5678", "1234"],
        "Сумма операции": [100, 200, 150]
    }
    df = pd.DataFrame(data)
    result = calculate_card_stats(df)
    expected = [
        {"Номер карты": "1234", "total_spent": 250, "cashback": 2.5, "last_digits": "1234"},
        {"Номер карты": "5678", "total_spent": 200, "cashback": 2.0, "last_digits": "5678"}
    ]
    assert result == expected


# Тест для функции get_currency_rates
@patch("requests.get")
def test_get_currency_rates(mock_get):
    mock_response = {
        "quotes": {
            "USDRUB": 75.0,
            "USDEUR": 0.9
        }
    }
    mock_get.return_value.json.return_value = mock_response
    currencies = ["USD", "EUR"]
    result = get_currency_rates(currencies)
    expected = [
        {'currency': 'USD', 'rate': 75.0},
        {'currency': 'EUR', 'rate': 83.33}  # 75.0 / 0.9 = 83.33
    ]
    assert result == expected


# Тест для функции get_stock_prices
@patch("yfinance.Ticker")
def test_get_stock_prices(mock_ticker):
    mock_stock = mock_ticker.return_value
    mock_data = pd.DataFrame({"Close": [150.0]}, index=[datetime(2024, 7, 19)])
    mock_stock.history.return_value = mock_data
    stocks = ["AAPL", "GOOGL"]
    result = get_stock_prices(stocks)
    expected = [
        {'stock': 'AAPL', 'price': 150.0},
        {'stock': 'GOOGL', 'price': 150.0}  # Проверка для двух акций с одинаковыми данными
    ]
    assert result == expected


# Тест для функции generate_report
@patch("src.views.load_user_settings", return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]})
@patch("src.views.filter_transactions")
@patch("src.views.calculate_card_stats")
@patch("src.views.get_top_transactions")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("pandas.read_excel")
def test_generate_report(mock_read_excel, mock_get_stock_prices, mock_get_currency_rates, mock_get_top_transactions,
                         mock_calculate_card_stats, mock_filter_transactions, mock_load_user_settings):
    mock_read_excel.return_value = pd.DataFrame({
        "Дата операции": ["01.01.2024 12:00:00", "15.01.2024 12:00:00"],
        "Сумма операции": [100, 200]
    })
    mock_filter_transactions.return_value = pd.DataFrame({
        "Дата операции": ["01.01.2024 12:00:00", "15.01.2024 12:00:00"],
        "Сумма операции": [100, 200]
    })
    mock_calculate_card_stats.return_value = [
        {"Номер карты": "1234", "total_spent": 300, "cashback": 3.0, "last_digits": "1234"}]
    mock_get_top_transactions.return_value = [{"Дата операции": "2024-01-15 12:00:00", "Сумма операции": 200}]
    mock_get_currency_rates.return_value = [{'currency': 'USD', 'rate': 75.0}]
    mock_get_stock_prices.return_value = [{'stock': 'AAPL', 'price': 150.0}]

    date = "2024-01-15 12:00:00"
    result = generate_report(date)

    expected = {
        "greeting": "Добрый день",  # Этот результат зависит от текущего времени, его можно изменить для тестов
        "cards": [{"Номер карты": "1234", "total_spent": 300, "cashback": 3.0, "last_digits": "1234"}],
        "top_transactions": [{"Дата операции": "2024-01-15 12:00:00", "Сумма операции": 200}],
        "currency_rates": [{'currency': 'USD', 'rate': 75.0}],
        "stock_prices": [{'stock': 'AAPL', 'price': 150.0}]
    }

    assert json.loads(result) == expected
