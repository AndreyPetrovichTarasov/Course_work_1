from src.utils import transactions
import json


print(transactions[:3])

with open("j_f.json", "w", encoding="utf-8") as f:
    json.dump(transactions[:3], f, ensure_ascii=False, indent=4)