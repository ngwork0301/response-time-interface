import pytest
from response_times import ResponseTimes


@pytest.fixture
def response_time_instance():
    """
    テスト対象のクラスのインスタンスを生成して返却
    正常系のデータを入れたtest.csvを入力に使用する。
    """
    return ResponseTimes("test.csv")


def test_find_failure(response_time_instance):
    """
    find_failureメソッドの正常系のテスト
    """
    expect = [{"address": "10.20.30.1/16",
               "period": "20221019133324-20221019133325"}]
    assert response_time_instance.find_failure() == expect
