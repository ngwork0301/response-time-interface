import pytest
import logging
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

def test_import_csv(caplog):
    """
    _import_csv()メソッドのテスト
    """
    caplog.set_level(logging.INFO)
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    expected_log_start = "Started importing csv: {0:}".format(test_csv_path)
    ResponseTimes(test_csv_path)
    assert ("response_times", logging.INFO, expected_log_start) in caplog.record_tuples
    assert ("response_times", logging.INFO, "Completed.") in caplog.record_tuples


def test_find_all_failure():
    """
    find_failureメソッドの正常系のテスト
    """
    # 1ホストで 1回だけ障害発生している場合のテスト
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    expect = [{"address": "10.20.30.1/16",
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"}]
    actual = ResponseTimes(test_csv_path).find_all_failure()
    
    assert actual == expect


def test_find_all_failure_threshold():
    """
    find_failureメソッドにthresholdを指定したときの正常系のテスト
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_4fail.csv")
    response_times = ResponseTimes(test_csv_path)
    threshold1_expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:25"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:26 ~ 2020-10-19 13:33:28"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:29 ~ 2020-10-19 13:33:32"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:33 ~ 2020-10-19 13:33:37"}
        ]
    actual = response_times.find_all_failure(threshold = 1)
    assert threshold1_expect == actual

    threshold3_expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:29 ~ 2020-10-19 13:33:32"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:33 ~ 2020-10-19 13:33:37"}
        ]
    actual = response_times.find_all_failure(threshold = 3)
    assert threshold3_expect == actual

    threshold5_expect = []
    actual = response_times.find_all_failure(threshold = 5)
    assert threshold5_expect == actual


def test_find_all_high_load():
    """
    find_high_loadメソッドの正常系のテスト
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_4sawtooth.csv")
    response_times = ResponseTimes(test_csv_path)
    expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:26 ~ 2020-10-19 13:33:31"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:34 ~ 2020-10-19 13:33:39"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:42 ~ 2020-10-19 13:33:47"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:50 ~ 2020-10-19 13:33:55"},
        ]
    actual = response_times.find_all_high_load(3, 3)
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
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"}]
    actual = response_times.find_all_subnet_failure(1)
    assert expect == actual
