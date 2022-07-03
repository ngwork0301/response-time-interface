import pytest
import logging
import os
from response_times import ResponseTimes


@pytest.fixture
def response_times_instance():
    """
    テスト対象のクラスのインスタンスを生成して返却
    データを入れたtest.csvを入力に使用する。
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
    find_failureメソッドのテスト
    """
    # 1ホストで 1回だけ障害発生している場合のテスト
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    expect = [{"address": "10.20.30.1/16",
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"}]
    actual = ResponseTimes(test_csv_path).find_all_failure()
    assert actual == expect
    
    # 1ホストで 複数回障害が発生している場合のテスト
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_4fail.csv")
    expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:25"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:26 ~ 2020-10-19 13:33:28"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:29 ~ 2020-10-19 13:33:32"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:33 ~ 2020-10-19 13:33:37"}
        ]
    actual = ResponseTimes(test_csv_path).find_all_failure()
    assert actual == expect

    # 2ホストで 複数回障害が発生している場合のテスト
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_2address_eachfail.csv")
    expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:25"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:26 ~ 2020-10-19 13:33:28"},
        {"address": "10.20.30.2/16", "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:25"},
        {"address": "10.20.30.3/16", "period": "2020-10-19 13:33:29 ~ 2020-10-19 13:33:30"}
        ]
    actual = ResponseTimes(test_csv_path).find_all_failure()
    assert actual == expect

def test_find_all_failure_threshold():
    """
    find_failureメソッドにthresholdを指定したときのテスト
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

    # threshold_countを3にしたとき、故障回数が減る
    threshold3_expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:29 ~ 2020-10-19 13:33:32"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:33 ~ 2020-10-19 13:33:37"}
        ]
    actual = response_times.find_all_failure(threshold = 3)
    assert threshold3_expect == actual

    # threshold_countを5にしたとき、故障なしになる
    assert len(response_times.find_all_failure(threshold = 5)) == 0


def test_find_all_high_load():
    """
    find_high_loadメソッドのテスト
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

    # threshold_averageを厳しくしたとき、期間が短くなる。
    expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:27 ~ 2020-10-19 13:33:30"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:35 ~ 2020-10-19 13:33:38"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:43 ~ 2020-10-19 13:33:46"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:51 ~ 2020-10-19 13:33:54"},
        ]
    actual = response_times.find_all_high_load(3, 4)
    assert expect == actual

    # threshold_averageを6にすると、過負荷がなしになる。
    assert len(response_times.find_all_high_load(3, 5)) == 0

    # threshold_countを減らせば、過負荷になる。
    expect = [
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:27 ~ 2020-10-19 13:33:28"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:35 ~ 2020-10-19 13:33:36"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:43 ~ 2020-10-19 13:33:44"},
        {"address": "10.20.30.1/16", "period": "2020-10-19 13:33:51 ~ 2020-10-19 13:33:52"},
        ]
    actual = response_times.find_all_high_load(1, 5)
    assert expect == actual


def test_find_subnet_failure():
    """
    find_subnet_failureメソッドのテスト
    """
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1subnet_2address_eachfail.csv")
    response_times = ResponseTimes(test_csv_path)
    expect = [{"subnet": "10.20.0.0/16",
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"}]
    actual = response_times.find_all_subnet_failure(1)
    assert expect == actual

    # 1サブネットに属する2つの以上のホストがリストにない場合は、サブネットの故障とはしない
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1address_1fail.csv")
    response_times = ResponseTimes(test_csv_path)
    assert len(response_times.find_all_subnet_failure()) == 0

    # 1サブネットに属する2つの以上のホストで片方しか故障していない場合は、サブネットの故障とはしない
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1subnet_2address_1sidefail.csv")
    response_times = ResponseTimes(test_csv_path)
    assert len(response_times.find_all_subnet_failure()) == 0

    # 障害発生時刻のずれが5秒以内のときは、サブネットの故障
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_1subnet_2address_eachfail_in_tolerance.csv")
    response_times = ResponseTimes(test_csv_path)
    expect = [{"subnet": "10.20.0.0/16",
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"}]
    actual = response_times.find_all_subnet_failure(1)
    assert expect == actual

    # 障害発生時刻のずれが6秒以上のときは、サブネットの故障としない
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_2subnet_2address_eachfail_out_tolerance.csv")
    response_times = ResponseTimes(test_csv_path)
    response_times = ResponseTimes(test_csv_path)
    assert len(response_times.find_all_subnet_failure()) == 0

    # 複数サブネットでの障害検知確認
    test_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_2subnet_eachfail.csv")
    response_times = ResponseTimes(test_csv_path)
    expect = [{"subnet": "10.20.0.0/16",
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"},
              {"subnet": "10.21.0.0/16",
               "period": "2020-10-19 13:33:24 ~ 2020-10-19 13:33:26"}]
    actual = response_times.find_all_subnet_failure(1)
    assert expect == actual
