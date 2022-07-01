import os
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

    def find_failure(self) -> list[dict[str, str]]:
        """
        故障状態のサーバーアドレスと、そのサーバーの故障期間を辞書に返却する。
        """
        result = []
        for address, records in self._records.items():
            is_failed = False  # レスポンスがない記録がはじまったフラグ
            fail_start_time = 0
            for log_datetime, response_time in sorted(records.items()):
                if not is_failed and response_time == '-':
                    fail_start_time = log_datetime
                    is_failed = True
                elif is_failed and response_time != '-':
                    fail_end_time = log_datetime
                    is_failed = False
                    period = "{0:}-{1:}".format(fail_start_time, fail_end_time)
                    result.append({
                        "address": address,
                        "period": period})
            else:
                # 応答が復帰したデータがみつからず最後に至ったら、最後の無応答時間までを故障期間にする。
                if is_failed:
                    period = "{0:}-{1:}".format(fail_start_time, log_datetime)
                    result.append({
                        "address": address,
                        "period": period})

        return result
