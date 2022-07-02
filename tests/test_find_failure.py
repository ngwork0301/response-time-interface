import pytest
import os
from response_times import ResponseTimes


@pytest.fixture
def response_times_instance():
    """
    テスト対象のクラスのインスタンスを生成して返却
    正常系のデータを入れたtest.csvを入力に使用する。
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    return ResponseTimes(test_csv_path)


def test_find_failure():
    """
    find_failureメソッドの正常系のテスト
    """
    # 1ホストで 1回だけ障害発生している場合のテスト
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    expect = [{"address": "10.20.30.1/16",
               "period": "20201019133324-20201019133326"}]
    actual = ResponseTimes(test_csv_path).find_failure()
    
    assert actual == expect


def test_find_failure_threshold():
    """
    find_failureメソッドにthresholdを指定したときの正常系のテスト
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_4fail.csv")
    response_times = ResponseTimes(test_csv_path)
    threshold1_expect = [
        {"address": "10.20.30.1/16", "period": "20201019133324-20201019133325"},
        {"address": "10.20.30.1/16", "period": "20201019133326-20201019133328"},
        {"address": "10.20.30.1/16", "period": "20201019133329-20201019133332"},
        {"address": "10.20.30.1/16", "period": "20201019133333-20201019133337"}
        ]
    actual = response_times.find_failure(threshold = 1)
    assert threshold1_expect == actual

    threshold3_expect = [
        {"address": "10.20.30.1/16", "period": "20201019133329-20201019133332"},
        {"address": "10.20.30.1/16", "period": "20201019133333-20201019133337"}
        ]
    actual = response_times.find_failure(threshold = 3)
    assert threshold3_expect == actual

    threshold5_expect = []
    actual = response_times.find_failure(threshold = 5)
    assert threshold5_expect == actual


def test_find_high_load():
    """
    find_high_loadメソッドの正常系のテスト
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_4sawtooth.csv")
    response_times = ResponseTimes(test_csv_path)
    expect = [
        {"address": "10.20.30.1/16", "period": "20201019133326-20201019133331"},
        {"address": "10.20.30.1/16", "period": "20201019133334-20201019133339"},
        {"address": "10.20.30.1/16", "period": "20201019133342-20201019133347"},
        {"address": "10.20.30.1/16", "period": "20201019133350-20201019133355"},
        ]
    actual = response_times.find_high_load(3, 3)
    assert expect == actual


def test_find_subnet_failure():
    """
    find_subnet_failureメソッドの正常系のテスト
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    response_times = ResponseTimes(test_csv_path)
    expect = [{"subnet": "10.20.0.0/16",
               "period": "20201019133324-20201019133326"}]
    actual = response_times.find_all_subnet_failure(1)
    assert expect == actual
