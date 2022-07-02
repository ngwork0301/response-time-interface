#!/usr/bin/env python
# -*- coding:utf-8-*-
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
    __slots__ = [
        '_records',
        '_subnets'
    ]

    def __init__(self, csv_file_path: str):
        self._records: dict[str, dict[int, str]] = {}
        self._subnets: dict[str, list[str]] = {}
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

        self._parse_subnet()

    def _parse_subnet(self):
        """
        アドレスからサブネットを特定して、サブネット内のアドレスの一覧を作成する。
        """
        def conv_ip_to_int(s_ip: str) -> int:
            splited = s_ip.split('.')
            result = int(splited[0])
            for idx in range(1, 4):
                result = result << 8
                result += int(splited[idx])
            return result

        def conv_int_to_ip(i_ip: int, i_mask_bits: int) -> str:
            result = "{0:}/{1:}".format(i_ip & 0xff, i_mask_bits)
            for idx in range(1, 4):
                result = "{0:}.".format((i_ip >> (8 * idx)) & 0xFF) + result
            return result
        
        def conv_bits_to_mask(i_bits) -> int:
            return ~sum([1 << idx for idx in range(i_bits)])

        def get_subnet(address: str) -> str:
            splited = address.split('/')
            if len(splited) == 2:
                i_ip = conv_ip_to_int(splited[0])
                i_mask_bits = int(splited[1])
                i_mask = conv_bits_to_mask(i_mask_bits)
                return conv_int_to_ip(i_ip & i_mask, i_mask_bits)
            elif len(splited) == 1:
                return address

        for address in self._records.keys():
            subnet = get_subnet(address)
            if subnet not in self._subnets:
                self._subnets[subnet] = []
            self._subnets[subnet].append(address)

    def _find_address_failure(self, address: str, threshold: int) -> list[dict[str, str]]:
        result = []
        records = self._records[address]
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

    def find_failure(self, threshold: int = 1) -> list[dict[str, str]]:
        """
        故障状態のサーバーアドレスと、そのサーバーの故障期間を返却する。
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

    def _find_subnet_failure(self, subnet: str, threshold: int = 1) -> list[dict[str, str]]:
        """
        指定したサブネットの故障期間を返却する。
        """
        def includes(address_failure: list, period: str) -> bool:
            for failure in address_failure:
                if period == failure['period']:
                    return True
            return False

        # サブネットに属する2つの以上のホストがリストにない場合は、サブネットの故障とはしない
        # if len(self._subnets[subnet]) < 2:
        #     return []
        # 最初のホストの故障期間データをもとに他のホストの故障を調べる
        first_address_failures = self._find_address_failure(self._subnets[subnet][0], threshold)
        result = [{"subnet": subnet, "period": failure["period"]} for failure in first_address_failures]
        for address in self._subnets[subnet]:
            address_failure = self._find_address_failure(address, threshold)
            result = list(filter(lambda r: includes(address_failure, r["period"]), result))
        return result

    def find_all_subnet_failure(self, threshold: int = 1) -> list[dict[str, str]]:
        """
        故障状態のサブネットと、その故障期間を返却する。
        """
        result = []
        for subnet in self._subnets.keys():
            result += self._find_subnet_failure(subnet, threshold)
        return result