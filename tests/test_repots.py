import pandas as pd
from datetime import datetime

# Пример даты
current_date = pd.to_datetime('2021-12-31 16:44:00')

# Вычитание трех месяцев с помощью DateOffset
three_months_ago = current_date - pd.DateOffset(months=3)

print(f"Current date: {current_date}")
print(f"Three months ago: {three_months_ago}")