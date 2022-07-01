import os
from typing import Optional
import functools


def is_datetime(s_arg: str) -> bool:
    """
    与えられた引数の文字列が日時の形式になっているかを確認する。
    """
    # TODO: ひとまず現状は自然数であればよいものとする。
    return is_natural_number(s_arg)


def is_natural_number(s_arg: str) -> bool:
    """
    与えられた引数の文字列が自然数（正の整数）になっているかを確認する。
    """
    try:
        i_arg = int(s_arg)
        if i_arg < 0:
            return False
    except ValueError:
        return False
    return True


def is_address(s_arg: str) -> bool:
    """
    与えられた引数の文字列がアドレスになっているかを確認する。
    """
    # TODO: 現象はすべてpass
    return True


class ResponseTimes(object):
    """
    時系列の応答時間データクラス
    """
    __slots__ = ['_records']

    def __init__(self, csv_file_path: str):
        self._records: dict[str, dict[int, str]] = {}
        self.read_csv(csv_file_path)

    def read_csv(self, file_path: str) -> None:
        """
        指定されたパスのCSVファイルを読み込む
        """
        def is_valid_csv(file_path: str) -> bool:
            if not os.path.isfile(file_path):
                return False
            return True

        def is_valid_line(line: str) -> bool:
            elements = line.split(',')
            if len(elements) >= 3:
                if not is_datetime(elements[0]):
                    return False
                if not is_address(elements[1]):
                    return False
            else:
                return False
            return True

        if is_valid_csv(file_path):
            with open(file_path, "r", encoding="utf-8") as fd:
                while True:
                    line = fd.readline()
                    if not line:
                        break
                    if is_valid_line(line):
                        elements = line.split(',')
                        log_datetime = int(elements[0].strip())
                        response_time = elements[2].strip()
                        address = elements[1].strip()
                        if address not in self._records:
                            self._records[address] = {}
                        self._records[address][log_datetime] = response_time

    def find_failure(self, threshold: int = 1) -> list[dict[str, str]]:
        """
        故障状態のサーバーアドレスと、そのサーバーの故障期間を辞書に返却する。
        """
        result = []
        if threshold <= 0:
            threshold = 1
        for address, records in self._records.items():
            failed_count = 0  # レスポンスがない記録の回数
            fail_start_time = 0
            for log_datetime, response_time in sorted(
                                  records.items(), key=lambda x: x[0]):
                if response_time == '-':
                    if failed_count <= 0:
                        fail_start_time = log_datetime
                    failed_count += 1
                elif failed_count >= 1:
                    fail_end_time = log_datetime
                    if failed_count >= threshold:
                        period = \
                            "{0:}-{1:}".format(fail_start_time, fail_end_time)
                        result.append({
                            "address": address,
                            "period": period})
                    failed_count = 0
            else:
                # 応答が復帰したデータがみつからず最後に至ったら、最後の無応答時間までを故障期間にする。
                if failed_count >= threshold:
                    period = "{0:}-{1:}".format(fail_start_time, log_datetime)
                    result.append({
                        "address": address,
                        "period": period})

        return result

    def find_high_load(self, threshold_count: int, threshold_average: float) -> list[dict[str, str]]:
        """
        直近threshold_count回の平均応答時間がthreshold_averageを超えていたら、
        そのサーバが過負荷になっているとみなし、その期間を取得する。
        """
        def average(response_times: list[str]) -> Optional[float]:
            only_num_list = list(filter(is_natural_number, response_times))
            if len(only_num_list) <= 0:
                return None
            total = functools.reduce(
                lambda x, y: str(int(x) + int(y)), only_num_list)
            return int(total) / len(only_num_list)

        result = []
        for address, records in self._records.items():
            sorted_records = sorted(records.items(), key=lambda x: x[0])
            # 直近threshold_count回分のデータ
            cached_responses = []

            load_start_time = 0
            for log_datetime, response_time in sorted_records:
                cached_responses.append(response_time)
                if len(cached_responses) > threshold_count:
                    cached_responses.pop(0)
                    recent_average = average(cached_responses)
                    if recent_average is not None \
                    and recent_average >= threshold_average:
                        if load_start_time <= 0:
                            load_start_time = log_datetime
                    elif load_start_time != 0:
                        load_end_time = log_datetime
                        period = \
                            "{0:}-{1:}".format(load_start_time, load_end_time)
                        result.append({
                            "address": address,
                            "period": period})
                        load_start_time = 0
            else:
                # 応答が復帰したデータがみつからず最後に至ったら、最後の無応答時間までを故障期間にする。
                if load_start_time != 0:
                    period = "{0:}-{1:}".format(load_start_time, log_datetime)
                    result.append({
                        "address": address,
                        "period": period})
        return result
