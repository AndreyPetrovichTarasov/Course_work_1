# from typing import List, Dict, Any
# from src.utils import list_for_investment
#
#
# def calculate_rounding_amount(amount, rounding_step):
#     """Функция рассчитывает сумму на инвесткопилку в зависимости от шага"""
#     return ((amount + rounding_step - 1) // rounding_step) * rounding_step - amount
#
#
# def investment_bank(month: str, all_transactions: List[Dict[str, Any]], limit: int) -> float:
#     """Функция расчитывает сумму, которую удалось бы отложить в «Инвесткопилку»."""
#     total_summ = 0
#     for i in  all_transactions:
#         if month in i["Дата операции"]:
#             total_summ += calculate_rounding_amount(i["Сумма операции"], limit)
#
#     return round(total_summ, 2)
#
#
# # Проверка функции
#
# if __name__ == "__main__":
#     print(investment_bank("2021-10", list_for_investment, 100))

import json
import logging
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, Dict, List

ROOT_PATH = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            Path(ROOT_PATH, "logs/services.log"), mode="w", encoding="utf-8"
        ),
    ],
)


def calculate_rounding_amount(amount: float, rounding_step: int) -> float:
    """Функция рассчитывает сумму на инвесткопилку в зависимости от шага"""
    # amount_decimal = Decimal(str(amount))
    # rounding_step_decimal = Decimal(rounding_step)
    # rounded_amount = (amount_decimal // rounding_step_decimal + 1) * rounding_step_decimal
    # rounding_amount = rounded_amount - amount_decimal
    # logging.info(f"Original amount: {amount}, Rounded amount: {rounded_amount}, Rounding amount: {rounding_amount}")
    # return float(rounding_amount)
    return ((amount + rounding_step - 1) // rounding_step) * rounding_step - amount


def parse_date(date_str: str) -> datetime:
    """Парсинг даты из строки с проверкой нескольких форматов"""
    date_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    raise ValueError(f"Date {date_str} does not match any of the expected formats")


def investment_bank(
    month: str, all_transactions: List[Dict[str, Any]], limit: int
) -> str:
    """Функция расчитывает сумму, которую удалось бы отложить в «Инвесткопилку»."""
    total_sum = Decimal("0.00")
    for transaction in all_transactions:
        transaction_date = parse_date(transaction["Дата операции"])
        if transaction_date.strftime("%Y-%m") == month:
            rounding_amount = calculate_rounding_amount(
                transaction["Сумма операции"], limit
            )
            total_sum += Decimal(str(rounding_amount))
            logging.info(
                f"Transaction Date: {transaction_date},"
                f" Amount: {transaction['Сумма операции']}, Rounding Amount: {rounding_amount}"
            )

    result = total_sum.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    logging.info(f"Total Sum for Investment Bank: {result}")

    response = {"month": month, "total_savings": float(result)}
    return json.dumps(response, ensure_ascii=False, indent=4)


# Проверка функции
if __name__ == "__main__":
    # print(investment_bank("2021-10", list_for_investment, 100))
    print(
        investment_bank(
            "2021-12",
            [
                {"Дата операции": "2021-12-31", "Сумма операции": 160.89},
                {"Дата операции": "2021-12-31", "Сумма операции": 64.0},
                {"Дата операции": "2021-12-31", "Сумма операции": 118.12},
            ],
            100,
        )
    )
