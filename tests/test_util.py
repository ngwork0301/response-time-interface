from tomlkit import integer
from response_times import is_datetime, is_positive_integer, is_address, is_response_time_result


def test_is_datetime():
    """
    is_datetime()関数のテスト
    """
    assert is_datetime("20201019133326") is True
    # 数値のみを許可
    assert is_datetime("2020101913332a") is False
    # マイナス、ドットも許可しない
    assert is_datetime("-02010191333.6") is False
    # ミリ秒を含むなど14桁より大きいものは許可しない
    assert is_datetime("202010191333261") is False
    # 0サブレスしてかならず14桁になっていること
    assert is_datetime("2020619133326") is False
    # エポック時間1970年1月1日より前
    assert is_datetime("19691019133326") is True
    # 0000年 は許可しない
    assert is_datetime("00001019133326") is False
    # 0001年は許可
    assert is_datetime("00011019133326") is True
    # 2038年以上を許可
    assert is_datetime("20381019133326") is True
    # 9999年も許可
    assert is_datetime("99991019133326") is True
    # 0月は非許可
    assert is_datetime("20200019133326") is False
    # 12月より大きい月は許可しない
    assert is_datetime("20201319133326") is False
    # 0日は非許可
    assert is_datetime("20201000133326") is False
    # 31日より大きい日は許可しない
    assert is_datetime("20201032133326") is False
    # 31日がない月は許可しない
    assert is_datetime("20200431133326") is False
    # うるう年(ある場合)
    assert is_datetime("20240229133326") is True
    # うるう年(ない場合)
    assert is_datetime("20230229133326") is False
    # 0時台は許可
    assert is_datetime("20201019003326") is True
    # 24時以上の時間は許可しない
    assert is_datetime("20201019243326") is False
    # 00分は許可
    assert is_datetime("20201019130026") is True
    # 60分以上は許可しない
    assert is_datetime("20201019136026") is False
    # 00秒は許可
    assert is_datetime("20201019130026") is True
    # 60秒以上は許可しない
    assert is_datetime("20201019136060") is False


def test_is_positive_integer():
    """
    is_positive_integer()関数のテスト
    """
    assert is_positive_integer('1') is True
    # 数値以外は許可しない
    assert is_positive_integer('a') is False
    # 小数も許可しない
    assert is_positive_integer('1.0') is False
    # 0は許可
    assert is_positive_integer('0') is True
    # 負の整数は許可しない
    assert is_positive_integer('-1') is False


def test_is_address():
    """
    is_address()関数のテスト
    """
    # サブネットマスクビット数つき
    assert is_address("10.20.30.1/16") is True
    # サブネットマスクビット数なしもサポート
    assert is_address("10.20.30.1") is True
    # サブネットマスクビット数が33ビット以上
    assert is_address("10.20.30.1/33") is False
    # IPv6アドレスは、現時点で非サポート
    assert is_address("1080:0:0:0:8:800:200C:417A") is False
    # 5オクテット目がある
    assert is_address("10.20.30.1.1/16") is False
    # 数値 → ipadress.IPv4Interfaceは許可するがここでは許可しない
    assert is_address(169090561) is False
    # マイナス値
    assert is_address(-1) is False
    # ホスト名も許可しない
    assert is_address("localhost") is False


def test_is_response_time_result():
    """
    is_response_time_result()関数のテスト
    """
    assert is_response_time_result("-") is True
    assert is_response_time_result("1") is True
    assert is_response_time_result("0") is True
    assert is_response_time_result("-1") is False

