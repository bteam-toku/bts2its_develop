from typing import TypedDict

class Mantis2RedmineParameters(TypedDict):
    """MantisBTからRedmineへの変換パラメータ
    """
    project_name: str               # プロジェクト名
    bts_prefix: str                 # BTSをフィルタするためのプレフィックス
    bts_base_url: str               # BTSベースURL
    date_range: int = 0             # 有効日付範囲（現在日からの過去日数）

