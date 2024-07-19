from src.views import generate_report
from src.reports import spending_by_category, save_report
from src.utils import transactions, list_df, list_for_investment
from src.services import investment_bank


print("Это страница главная")
print(generate_report("2021-12-31 15:30:00"))
print()

print("Это инвесткопилка")
print(investment_bank("2021-10", list_for_investment, 100))
print()

print("Это отчет по категориям")
print(spending_by_category(list_df, "Супермаркеты", "31.12.2018 16:39:04"))
# print(spending_by_category(list_df, "Супермаркеты"))

