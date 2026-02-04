from bts2its.interfaces import AbstractBts2Its
from bts2its.common import *
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

class BaseMantis2Redmine(AbstractBts2Its):
    """MantisBTからRedmineへの変換基底クラス
    """
    #
    # public定数
    #
    FIXED_KEYWORDS = {                             # 固定キーワードマッピング
        # BTS側キーワード
        'bts_id':'Id',
        'bts_title':'要約',
        'bts_status':'ステータス',
        'bts_version':'修正予定バージョン',
        'bts_date':'更新日',
        # ITS側キーワード
        'its_operation':'操作',
        'its_id':'#',
        'its_tracker':'トラッカー',
        'its_parent_id':'親チケット',
        'its_status':'ステータス',
        'its_title':'題名',
        'its_author':'作成者',
        'its_assigned_to':'担当者',
        'its_update_date':'更新日',
        'its_category':'カテゴリ',
        'its_target_version':'対象バージョン',
        'its_start_date':'開始日',
        'its_due_date':'期日',
        'its_estimated_hours':'予定工数',
        'its_total_estimated_hours':'合計予定工数',
        'its_spent_hours':'作業工数',
        'its_total_spent_hours':'合計作業工数',
        'its_done_ratio':'進捗率',
        'its_created_on':'作成日',
        'its_closed_on':'終了日',
        'its_priority':'優先度',
        'its_description':'説明',
        # ITS側固定値
        'its_operation_add':'登録',
        'its_operation_update':'更新',
        'its_status_open':'新規',
        'its_status_close':'終了',
    }

    #
    # protected変数
    #

    _parameters: Mantis2RedmineParameters = None    # MantisBTからRedmineへの変換パラメータ
    #
    # protected定数
    #
    _BTS_DATA_COLUMNS = [                           # BTSデータカラム
        FIXED_KEYWORDS['bts_id'],
        FIXED_KEYWORDS['bts_title'],
        FIXED_KEYWORDS['bts_status'],
        FIXED_KEYWORDS['bts_version'],
        FIXED_KEYWORDS['bts_date'],
    ]
    _BTS_CLOSED_STATUS = []                         # BTS終了ステータスリスト
    _ITS_DATA_COLUMNS = []                          # ITSデータカラム
    _ITS_ENTRY_COLUMNS = [                          # ITS起票データカラム
        FIXED_KEYWORDS['its_operation'],
        FIXED_KEYWORDS['its_id'], 
        FIXED_KEYWORDS['its_tracker'],
        FIXED_KEYWORDS['its_parent_id'],
        FIXED_KEYWORDS['its_status'],
        FIXED_KEYWORDS['its_title'],
        FIXED_KEYWORDS['its_author'],
        FIXED_KEYWORDS['its_assigned_to'],
        FIXED_KEYWORDS['its_update_date'],
        FIXED_KEYWORDS['its_category'],
        FIXED_KEYWORDS['its_target_version'],
        FIXED_KEYWORDS['its_start_date'],
        FIXED_KEYWORDS['its_due_date'],
        FIXED_KEYWORDS['its_estimated_hours'],
        FIXED_KEYWORDS['its_total_estimated_hours'],
        FIXED_KEYWORDS['its_spent_hours'],
        FIXED_KEYWORDS['its_total_spent_hours'],
        FIXED_KEYWORDS['its_done_ratio'],
        FIXED_KEYWORDS['its_created_on'],
        FIXED_KEYWORDS['its_closed_on'],
        FIXED_KEYWORDS['its_priority'],
        FIXED_KEYWORDS['its_description'],                  
    ]
    _ITS_PARENT_TICKET_TITLE = []                   # ITS親チケットタイトルリスト
    _ITS_CLOSED_STATUS = []                         # ITS終了ステータスリスト
    _ITS_TITLE_FORMAT = '{}[{}:{}]'                 # ITS起票タイトルフォーマット

    #
    # コンストラクタ/デストラクタ
    #
    def __init__(self, parameters: Mantis2RedmineParameters) -> None:
        """コンストラクタ

        Args:
            parameters (Mantis2RedmineParameters): MantisBTからRedmineへの変換パラメータ
        """
        super().__init__()
        self._parameters = parameters

    def __del__(self) -> None:
        """デストラクタ
        """
        super().__del__()

    #
    # publicメソッド
    #
    def load_bts(self, file_path: Path) -> None:
        """バグ管理データ読み取り

        Args:
            file_path (Path): データのファイルパス
        """
        self._pd_bts = self._load_mantis(file_path)

    def load_its(self, file_path: Path) -> None:
        """Issue管理データ読み取り

        Args:
            file_path (Path): データのファイルパス
        """
        self._pd_its = self._load_redmine(file_path)

    def bts_to_its(self) -> None:
        """BTSからITSへの起票データ作成
        """
        pass

    def get_its_entry_data(self) -> pd.DataFrame:
        """ITSの起票データ取得

        Returns:
            pd.DataFrame: Pandas.DataFrame型
        """
        return self._pd_its_entry

    #
    # protectedメソッド
    #
    def _load_mantis(self, file_path: Path) -> pd.DataFrame:
        """MantisBTデータのロード

        Args:
            file_path (Path): MantisBTのExportデータファイルパス

        Returns:
            pd.DataFrame: MantisBTデータDataFrame
        """
        columns = self._BTS_DATA_COLUMNS.copy() if len(self._BTS_DATA_COLUMNS) > 0 else None    
        return pd.read_csv(file_path, usecols=columns, encoding='utf-8-sig', encoding_errors='replace')
    
    def _load_redmine(self, file_path: Path) -> pd.DataFrame:
        """Redmineデータのロード

        Args:
            file_path (Path): RedmineのExportデータファイルパス

        Returns:
            pd.DataFrame: RedmineデータDataFrame
        """
        columns = self._ITS_DATA_COLUMNS.copy() if len(self._ITS_DATA_COLUMNS) > 0 else None
        return pd.read_csv(file_path, usecols=columns, encoding='utf-8-sig', encoding_errors='replace')
    
    def _get_bts_version(self, bts_row: pd.Series) -> str:
        """BTSのバージョン情報取得

        Args:
            bts_row (pd.Series): BTSデータ行

        Returns:
            str: BTSのバージョン情報文字列
        """
        bts_version = str(bts_row[self.FIXED_KEYWORDS['bts_version']] if pd.isna(bts_row[self.FIXED_KEYWORDS['bts_version']]) is False else '')
        return bts_version
    
    def _get_bts_status(self, bts_row: pd.Series) -> str:
        """BTSのステータス情報取得

        Args:
            bts_row (pd.Series): BTSデータ行

        Returns:
            str: BTSのステータス情報文字列
        """
        bts_status = str(bts_row[self.FIXED_KEYWORDS['bts_status']])
        return bts_status
    
    def _get_bts_url(self, bts_row: pd.Series) -> str:
        """BTSのURL情報取得

        Args:
            bts_row (pd.Series): BTSデータ行

        Returns:
            str: BTSのURL情報文字列
        """
        bts_url = self._parameters['bts_base_url'] + str(bts_row[self.FIXED_KEYWORDS['bts_id']])
        return bts_url

    def _get_its_parent_ticket(self) -> list:
        """ITS親チケットリスト取得

        _ITS_PARENT_TICKET_TITLEに設定されたタイトルからチケットを取得する。

        Returns:
            list: ITS親チケットリスト
        """
        # 親チケットの指定がない場合は空リストを返す
        if self._ITS_PARENT_TICKET_TITLE is None or len(self._ITS_PARENT_TICKET_TITLE) == 0:
            print('ITS parent ticket title not specified.')
            return []
        # ITSデータが存在しない場合は空リストを返す
        if self._pd_its is None or self._pd_its.empty is True:
            print('ITS data not loaded.')
            return []

        # 親チケットリストを取得
        global title
        parent_row = [self._pd_its.query('題名 == @title') for title in self._ITS_PARENT_TICKET_TITLE]
        # 親チケットが存在しない場合は空リストを返す
        if all(row.empty is True for row in parent_row):
            return []
        # 親チケットリストを返す
        return parent_row
    
    def _within_date_range(self, date_str: str) -> bool:
        """指定日付が対象期間内か判定

        Args:
            date_str (str): BTS更新日付文字列

        Returns:
            bool: 対象期間内の場合True、対象期間外の場合False
        """
        try :
            # 日付範囲指定がマイナスの場合は全期間を対象として常にTrueを返す
            if self._parameters['date_range'] < 0 :
                return True

            # 対象期間開始日とBTS更新日を計算 
            target_start_date = datetime.now() - timedelta(days=self._parameters['date_range'])
            update_date = pd.to_datetime(date_str)
            # BTS更新日が対象期間外の場合はFalseを返す
            if pd.isna(update_date) or update_date < target_start_date:
                return False
            return True
        except :
            # 日付変換エラーの場合はFalseを返す
            return False
