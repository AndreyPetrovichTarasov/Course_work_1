import pandas as pd
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Callable
from src.utils import list_df
from src.utils import convert_date_format

ROOT_PATH = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(Path(ROOT_PATH, "logs/repots.log"), mode='w', encoding='utf-8'),
    ]
)


def save_report(file_name: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if file_name:
                output_file = file_name
            else:
                output_file = "default_report.json"
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(result)
            return result

        return wrapper

    return decorator


@save_report("custom_report.json")
# @save_report()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """Сортировка списка словарей по дате и категориям"""
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    if date is None:
        last_date = transactions["Дата операции"].max()
        three_months_ago = last_date - pd.DateOffset(months=3)

        filtered_df = transactions[
            (transactions['Дата операции'] >= three_months_ago) & (transactions['Дата операции'] <= last_date)]
        filtered = filtered_df[filtered_df['Категория'] == category]
        logging.info("Фильтрация по категориям по последней дате")
    else:
        user_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
        three_months_ago = user_date - pd.DateOffset(months=3)

        filtered_df = transactions[
            (transactions['Дата операции'] >= three_months_ago) & (transactions['Дата операции'] <= user_date)]
        filtered = filtered_df[filtered_df['Категория'] == category]
        logging.info("Фильтрация по категориям по указанной дате")
    json_data = filtered.to_json(orient="records", force_ascii=False)

    return json_data


if __name__ == "__main__":
    print(list_df)
    # print(spending_by_category(list_df, "Супермаркеты", "31.12.2018 16:39:04"))
    # print(spending_by_category(list_df, "Супермаркеты"))
