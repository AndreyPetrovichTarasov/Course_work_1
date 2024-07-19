import pytest
import pandas as pd
import json
import os
from datetime import datetime
from typing import Optional, Callable
from src.reports import save_report, spending_by_category


@pytest.fixture
def transactions_data():
    data = {
        "Дата операции": ["01.01.2022 12:00:00", "02.02.2022 13:00:00", "03.03.2022 14:00:00"],
        "Категория": ["еда", "транспорт", "еда"],
        "Сумма": [100, 200, 150]
    }

    return pd.DataFrame(data)


def test_spending_by_category(transactions_data):
    result = spending_by_category(transactions_data, "еда")
    expected_data = [
        {"Дата операции": "2022-01-01T12:00:00.000Z", "Категория": "еда", "Сумма": 100},
        {"Дата операции": "2022-03-03T14:00:00.000Z", "Категория": "еда", "Сумма": 150}
    ]
    expected_result = json.dumps(expected_data, ensure_ascii=False)

    # Преобразуйте даты в ожидаемом результате в Unix timestamp
    expected_result_data = json.loads(expected_result)
    for item in expected_result_data:
        item["Дата операции"] = int(pd.to_datetime(item["Дата операции"]).timestamp() * 1000)

    expected_result = json.dumps(expected_result_data, ensure_ascii=False, separators=(',', ':'))

    assert result == expected_result


def test_save_report_decorator(transactions_data, tmpdir):
    file_name = tmpdir.join("test_report.json")
    decorated_function = save_report(str(file_name))(spending_by_category)

    result = decorated_function(transactions_data, "еда")

    assert os.path.exists(file_name)

    with open(file_name, "r", encoding="utf-8") as file:
        file_content = file.read()
        assert file_content == result
