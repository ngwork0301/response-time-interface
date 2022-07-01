import pytest
import os
from response_times import ResponseTimes


@pytest.fixture
def response_time_instance():
    """
    テスト対象のクラスのインスタンスを生成して返却
    正常系のデータを入れたtest.csvを入力に使用する。
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test.csv")
    return ResponseTimes(test_csv_path)

def test_find_failure(response_time_instance):
    """
    find_failureメソッドの正常系のテスト
    """
    expect = [{"address": "10.20.30.1/16",
               "period": "20201019133324-20201019133326"}]
    
    assert response_time_instance.find_failure() == expect
