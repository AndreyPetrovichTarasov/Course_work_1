from typing import List, Dict, Any
from src.utils import list_for_investment


def calculate_rounding_amount(amount, rounding_step):
    """Функция рассчитывает сумму на инвесткопилку в зависимости от шага"""
    return ((amount + rounding_step - 1) // rounding_step) * rounding_step - amount


def investment_bank(month: str, all_transactions: List[Dict[str, Any]], limit: int) -> float:
    """Функция расчитывает сумму, которую удалось бы отложить в «Инвесткопилку»."""
    total_summ = 0
    for i in  all_transactions:
        if month in i["Дата операции"]:
            total_summ += calculate_rounding_amount(i["Сумма операции"], limit)

    return round(total_summ, 2)


# Проверка функции

if __name__ == "__main__":
    print(investment_bank("2021-10", list_for_investment, 100))
