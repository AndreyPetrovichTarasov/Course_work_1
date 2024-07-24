import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Hashable, Optional

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from src.utils import (load_user_settings, get_greeting, filter_transactions, calculate_card_stats,
                       get_top_transactions, get_currency_rates, get_stock_prices, df)

load_dotenv()

api_key = os.getenv("API_KEY")

ROOT_PATH = Path(__file__).resolve().parent.parent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            Path(ROOT_PATH, "logs/repots.log"), mode="w", encoding="utf-8"
        ),
    ],
)


def generate_report(dataframe: pd.DataFrame) -> str:
    """Создание финального отчета для пользователя"""
    datetime_str = dataframe['datetime'].iloc[0]
    settings = load_user_settings()
    user_currencies = settings.get("user_currencies", [])
    user_stocks = settings.get("user_stocks", [])

    transactions = pd.read_excel(Path(ROOT_PATH, "data/operations.xlsx"))

    filtered_transactions = filter_transactions(transactions, datetime_str)

    card_stats = calculate_card_stats(filtered_transactions)

    top_transactions = get_top_transactions(filtered_transactions)

    currency_rates = get_currency_rates(user_currencies)

    stock_prices = get_stock_prices(user_stocks)

    current_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    greeting = get_greeting(current_time)

    report = {
        "greeting": greeting,
        "cards": card_stats,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    logging.info("Формирование финального отчета для пользователя")

    return json.dumps(report, ensure_ascii=False, indent=4)


# Пример вызова функции
if __name__ == "__main__":
    print(generate_report(df))
