import os
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

api_key = os.getenv('API_KEY')

ROOT_PATH = Path(__file__).resolve().parent.parent


def load_user_settings(file_path: str = 'user_settings.json') -> Dict[str, List[str]]:
    with open(file_path, 'r', encoding='utf-8') as file:
        settings = json.load(file)
    return settings


def get_greeting(current_time: datetime) -> str:
    hour = current_time.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def filter_transactions(transactions: pd.DataFrame, date: str) -> pd.DataFrame:
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1)

    # Создаем явную копию DataFrame
    transactions = transactions.copy()

    # Используем .loc для явного указания изменений
    transactions.loc[:, "Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    return transactions[(transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)]


def calculate_card_stats(filtered_transactions: pd.DataFrame) -> List[Dict[str, float]]:
    card_stats = filtered_transactions.groupby('Номер карты').agg(
        total_spent=('Сумма операции', 'sum'),
        cashback=('Сумма операции', (lambda x: round(x.sum() / 100, 2)))
    ).reset_index()
    card_stats['last_digits'] = card_stats['Номер карты'].astype(str).str[-4:]
    return card_stats.to_dict(orient='records')


def get_top_transactions(filtered_transactions: pd.DataFrame, top_n: int = 5) -> List[Dict[str, str]]:
    filtered_transactions["Дата операции"] = pd.to_datetime(filtered_transactions["Дата операции"],
                                                            format="%Y-%m-%d %H:%M:%S").dt.strftime('%Y-%m-%d %H:%M:%S')
    top_transactions = filtered_transactions.nlargest(top_n, 'Сумма операции')
    return top_transactions.to_dict(orient='records')


def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    symbols = ",".join(currencies)

    url = f'https://api.apilayer.com/currency_data/live?symbols={symbols}'
    headers = {"apikey": api_key}

    response = requests.get(url, headers=headers)

    data = response.json()

    quotes = data.get('quotes', {})
    usd_to_rub = quotes.get('USDRUB')
    usd_to_eur = quotes.get('USDEUR')
    rub_to_eur = usd_to_rub / usd_to_eur

    return [
        {'currency': 'USD', 'rate': round(usd_to_rub, 2)},
        {'currency': 'EUR', 'rate': round(rub_to_eur, 2)}
    ]


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    stock_prices = []
    for my_stock in stocks:
        stock = yf.Ticker(my_stock)
        data = stock.history(period="1d")

        # Преобразуем JSON строку в объект Python (словарь)
        json_data = json.loads(data.to_json(orient="index"))

        # Получаем цену закрытия для последнего доступного дня
        price = json_data[list(json_data.keys())[0]]['Close']

        stock_prices.append({'stock': my_stock, 'price': round(price, 2)})

    return stock_prices


def generate_report(date: str) -> str:
    settings = load_user_settings()
    user_currencies = settings.get("user_currencies", [])
    user_stocks = settings.get("user_stocks", [])

    transactions = pd.read_excel(Path(ROOT_PATH, "data/operations.xlsx"))

    filtered_transactions = filter_transactions(transactions, date)

    card_stats = calculate_card_stats(filtered_transactions)

    top_transactions = get_top_transactions(filtered_transactions)

    currency_rates = get_currency_rates(user_currencies)

    stock_prices = get_stock_prices(user_stocks)

    current_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    greeting = get_greeting(current_time)

    report = {
        "greeting": greeting,
        "cards": card_stats,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(report, ensure_ascii=False, indent=4)


# Пример вызова функции
if __name__ == "__main__":
    print(generate_report("2021-12-31 15:30:00"))
