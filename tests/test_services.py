import pytest
import json
from src.services import investment_bank


def test_investment_bank():
    result = investment_bank("2021-12", [{'Дата операции': '2021-12-31', 'Сумма операции': 160.89},
                                       {'Дата операции': '2021-12-31', 'Сумма операции': 64.0},
                                       {'Дата операции': '2021-12-31', 'Сумма операции': 118.12}],100)
    expected_result = {"month": "2021-12", "total_savings": 156.99}
    expected_result_json = json.dumps(expected_result, indent=4)
    assert result == expected_result_json


