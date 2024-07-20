import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Hashable

import pandas as pd

from config import path_xlsx

ROOT_PATH = Path(__file__).resolve().parent.parent

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

if __name__ == "__main__":
    # print(transactions[:5])
    print(list_for_investment[:3])
    # print(list_to_df(transactions[:5]))
    # print(transactions[:5])
