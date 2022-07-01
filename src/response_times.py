class ResponseTimes(object):
    def __init__(self, csv_file_path : str):
        pass

    def find_failure(self) -> list[dict[str, str]]:
        """
        故障状態のサーバーアドレスと、そのサーバーの故障期間を辞書に返却する。
        """
        return [{"address": "10.20.30.1/16", "period": "20221019133324-20221019133325"}]
