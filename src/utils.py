import json
import os
import logging
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
from typing import Dict, List, Any, Hashable, Optional
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict, List, Hashable
from config import path_xlsx

ROOT_PATH = Path(__file__).resolve().parent.parent

load_dotenv()

api_key = os.getenv("API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            Path(ROOT_PATH, "logs/utils.log"), mode="w", encoding="utf-8"
        ),
    ],
)


def from_xlsx() -> list[dict[Hashable, Any]]:
    """Преобразование из эксель-файла в python-объект"""
    df = pd.read_excel(Path(ROOT_PATH, path_xlsx))
    logging.error("File not found")
    list_of_dicts = df.to_dict(orient="records")

    return list_of_dicts


def list_to_df(list_transactions: List[Dict[Hashable, Any]]) -> pd.DataFrame:
    """Преобразование списка словарей в объект DataFrame"""
    df_list = pd.DataFrame(list_transactions)

    return df_list


def investment_dict(
        transactions_for_invest: List[Dict[Hashable, Any]]
) -> list[dict[Hashable, Any]]:
    """Сортировка по ключам Дата и Сумма операции"""
    keys_to_keep = ["Дата операции", "Сумма операции"]
    list_for_invest = [
        {k: v for k, v in d.items() if k in keys_to_keep}
        for d in transactions_for_invest
    ]
    logging.info("Формирование словаря списков")
    return list_for_invest


def convert_date_format(date_str: str) -> str:
    """Преобразование формата времени"""
    date_obj = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

    return date_obj.strftime("%Y-%m-%d")


transactions = from_xlsx()

list_for_investment = [
    {
        "Дата операции": convert_date_format(item["Дата операции"]),
        "Сумма операции": abs(item["Сумма операции"]),
    }
    for item in investment_dict(transactions)
]

list_df = list_to_df(transactions)


def load_user_settings(file_path: str = "user_settings.json") -> Dict[str, List[str]]:
    """Считывание настроек пользователя"""
    with open(file_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
        logging.error("File not found")
    return settings


def get_greeting(current_time: Optional[datetime] = None) -> str:
    """Обработка блока Приветствие"""
    if current_time is None:
        current_time = datetime.now()
        logging.info(f"Преобразование даты: {current_time}")
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
    """Фильтрация транзакций по дате"""
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1)

    # Создаем явную копию DataFrame
    transactions = transactions.copy()

    # Используем .loc для явного указания изменений
    transactions.loc[:, "Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    logging.info("Фильтрация транзакций")

    return transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
        ]


def calculate_card_stats(filtered_transactions: pd.DataFrame) -> List[Dict[Hashable, Any]]:
    """Подсчет суммы операций и кэшбека по картам"""
    card_stats = (
        filtered_transactions.groupby("Номер карты")
        .agg(
            total_spent=("Сумма операции", "sum"),
            cashback=("Сумма операции", (lambda x: abs(round(x.sum() / 100, 2)))),
        )
        .reset_index()
    )
    card_stats["last_digits"] = card_stats["Номер карты"].astype(str).str[-4:]
    logging.info("Формирование транзакций по картам")

    return card_stats.to_dict(orient="records")


def get_top_transactions(
        filtered_transactions: pd.DataFrame, top_n: int = 5
) -> list[dict[Hashable, Any]]:
    """Филтрация последних 5 транзакций"""
    filtered_transactions["Дата операции"] = pd.to_datetime(
        filtered_transactions["Дата операции"], format="%Y-%m-%d %H:%M:%S"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    top_transactions = filtered_transactions.nlargest(top_n, "Сумма операции")
    logging.info("Получение последних 5 транзакций")
    return top_transactions.to_dict(orient="records")


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получение по АПИ курсов валют"""
    symbols = ",".join(currencies)

    url = f"https://api.apilayer.com/currency_data/live?symbols={symbols}"
    headers = {"apikey": api_key}

    response = requests.get(url, headers=headers)
    logging.error("Ошибка соединения с сервером")

    data = response.json()

    quotes = data.get("quotes", {})
    usd_to_rub = quotes.get("USDRUB")
    usd_to_eur = quotes.get("USDEUR")
    rub_to_eur = usd_to_rub / usd_to_eur
    logging.info("Формирование курса валют")

    return [
        {"currency": "USD", "rate": round(usd_to_rub, 2)},
        {"currency": "EUR", "rate": round(rub_to_eur, 2)},
    ]


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """Получение по АПИ курсов акций"""
    stock_prices = []
    for my_stock in stocks:
        stock = yf.Ticker(my_stock)
        data = stock.history(period="1d")
        json_data = json.loads(data.to_json(orient="index"))
        # Получаем цену закрытия для последнего доступного дня
        price = json_data[list(json_data.keys())[0]]["Close"]

        stock_prices.append({"stock": my_stock, "price": round(price, 2)})
    logging.info("Формирование курса акций")

    return stock_prices


def df_for_main():
    """Создание датафрейм"""
    datetime_str = "2021-12-31 15:30:00"

    date_frame = pd.DataFrame({'datetime': [datetime_str]})

    return date_frame


df = df_for_main()

if __name__ == "__main__":
    # print(transactions[:5])
    print(list_for_investment[:3])
    # print(list_to_df(transactions[:5]))
    # print(transactions[:5])
