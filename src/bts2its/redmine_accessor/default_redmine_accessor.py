from its_accessor import BaseRedmineAccessor

class DefaultRedmineAccessor(BaseRedmineAccessor):
    """Redmineアクセスクラス
    デフォルトの具象化クラス
    """
    #
    # public members
    #
    # RedmineのIssue作成ペイロードテンプレート
    its_payload_template:dict = {
        '#': '',
        'トラッカー': '',
        '親チケット': '',
        'ステータス': '',
        '題名': '',
        '担当者': '',
        '対象バージョン': '',
        '開始日': '',
        '期日': '',
        '予定工数': '',
        '合計予定工数': '',
        '作業時間': '',
        '合計作業時間': '',
        '進捗率': '',
        '優先度': '',
        '説明': '',
    }
