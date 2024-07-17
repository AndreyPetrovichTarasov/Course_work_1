from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT_PATH = Path(__file__).resolve().parent.parent


def from_xlsx():
    """Преобразование из эксель-файла в python-объект"""
    df = pd.read_excel(Path(ROOT_PATH, "data/operations.xlsx"))

    list_of_dicts = df.to_dict(orient='records')

    return list_of_dicts


def list_to_df(list_transactions):
    df_list = pd.DataFrame(list_transactions)

    return df_list


def investment_dict(transactions_for_invest):
    keys_to_keep = ["Дата операции", "Сумма операции"]
    list_for_invest = [{k: v for k, v in d.items() if k in keys_to_keep} for d in transactions_for_invest]

    return list_for_invest


def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
    return date_obj.strftime('%Y-%m-%d')


transactions = from_xlsx()

list_for_investment = [
    {
        'Дата операции': convert_date_format(item['Дата операции']),
        'Сумма операции': abs(item['Сумма операции'])
    }
    for item in investment_dict(transactions)
]


if __name__ == "__main__":
    # print(transactions[:5])
    # print(list_for_investment[:3])
    print(list_to_df(transactions[:5]))