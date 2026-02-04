from bts2its.mantis2redmine import BaseMantis2Redmine
from bts2its.common import *
from pathlib import Path
import pandas as pd
import re
from datetime import datetime, timedelta

class DefaultMantis2Redmine(BaseMantis2Redmine):
    """MantisBTからRedmineへの変換デフォルトクラス
    """
    #
    # コンストラクタ/デストラクタ
    #
    def __init__(self, parameters: Mantis2RedmineParameters) -> None:
        """コンストラクタ
        """
        #_BTS_CLOSED_STATUSにカラムを追加
        self._BTS_CLOSED_STATUS = super()._BTS_CLOSED_STATUS + [
            '解決済',
            '修正済',
            '完了'
        ]
        # _ITS_CLOSED_STATUSにカラムを追加
        self._ITS_CLOSED_STATUS = super()._ITS_CLOSED_STATUS + [
            '終了',
            '却下',
        ]
        # スーパークラスのコンストラクタ呼び出し
        super().__init__(parameters)

    def __del__(self) -> None:
        """デストラクタ
        """
        super().__del__()

    #
    # publicメソッド
    #
    def bts_to_its(self) -> None:
        """BTSからITSへの起票データ作成
        """
        # 親チケットを取得
        parent_row = self._get_its_parent_ticket()
        if all(row.empty is True for row in parent_row):
            return
        
        # mantisからredmineに登録
        output_new_rows = []
        new_row = {col: '' for col in self._ITS_ENTRY_COLUMNS}
        for _, bts_row in self._pd_bts.iterrows():
            # BTS更新日が対象期間外の場合はスキップ
            if self._within_date_range(str(bts_row[self.FIXED_KEYWORDS['bts_date']])) is False:
                continue

            # BTSのバージョン情報を取得
            mantis_version = self._get_bts_version(bts_row)
            # BTSのステータス情報を取得
            mantis_status = self._get_bts_status(bts_row)
            # BTSのURL情報を取得
            mantis_url = self._get_bts_url(bts_row)

            # ITSの該当チケットリストを取得
            target_redmine_row = None
            parent_id = ''
            for i, row in enumerate(parent_row):
                if not row.empty:
                    # 親チケットIDを取得
                    parent_id = row.at[row.index[0], self.FIXED_KEYWORDS['its_id']]
                    # ITS題名のフォーマットに基づき該当チケットを検索
                    target_redmine_title = self._ITS_TITLE_FORMAT.format(self._ITS_PARENT_TICKET_TITLE[i], bts_row[self.FIXED_KEYWORDS['bts_id']], bts_row[self.FIXED_KEYWORDS['bts_title']])
                    target_redmine_row = self._pd_its[self._pd_its[self.FIXED_KEYWORDS['its_title']].str.startswith(target_redmine_title)]
                    break

            # 新規登録（該当チケットが存在しない場合）
            if target_redmine_row is None or target_redmine_row.empty:
                # 操作を設定（修正予定バージョンが未設定は登録しない）
                param_operation = self.FIXED_KEYWORDS['its_operation_add'] if mantis_version != '' else ''
                # ステータスを設定
                param_status = self.FIXED_KEYWORDS['its_status_close'] if mantis_version in self._BTS_CLOSED_STATUS else self.FIXED_KEYWORDS['its_status_open']
                # ROW追加
                new_row.clear()
                new_row.update({
                    self.FIXED_KEYWORDS['its_operation']:param_operation,
                    self.FIXED_KEYWORDS['its_id']:'',
                    self.FIXED_KEYWORDS['its_tracker']:'エントリー対応',
                    self.FIXED_KEYWORDS['its_parent_id']:parent_id,
                    self.FIXED_KEYWORDS['its_status']:param_status,
                    self.FIXED_KEYWORDS['its_title']:target_redmine_title,
                    self.FIXED_KEYWORDS['its_author']:'',
                    self.FIXED_KEYWORDS['its_assigned_to']:'',
                    self.FIXED_KEYWORDS['its_update_date']:'',
                    self.FIXED_KEYWORDS['its_category']:'',
                    self.FIXED_KEYWORDS['its_target_version']:mantis_version,
                    self.FIXED_KEYWORDS['its_start_date']:'',
                    self.FIXED_KEYWORDS['its_due_date']:'',
                    self.FIXED_KEYWORDS['its_estimated_hours']:'0',
                    self.FIXED_KEYWORDS['its_total_estimated_hours']:'',
                    self.FIXED_KEYWORDS['its_spent_hours']:'',
                    self.FIXED_KEYWORDS['its_total_spent_hours']:'',
                    self.FIXED_KEYWORDS['its_done_ratio']:'',
                    self.FIXED_KEYWORDS['its_created_on']:'',
                    self.FIXED_KEYWORDS['its_closed_on']:'',
                    self.FIXED_KEYWORDS['its_priority']:'通常',
                    self.FIXED_KEYWORDS['its_description']:mantis_url
                })
                output_new_rows.append(new_row.copy())
                
            # 更新処理（該当チケットが存在する場合）
            else:
                # ステータス更新は子から処理する必要があるため、IDの降順にソート
                sorted_target_redmine_row = target_redmine_row.sort_values(by=self.FIXED_KEYWORDS['its_id'], ascending=False)

                #　該当チケット毎に更新処理
                for _, redmine_row in sorted_target_redmine_row.iterrows():
                    # 更新可否判定用にredmineのバージョン・ステータスを取得
                    redmine_version = str(redmine_row[self.FIXED_KEYWORDS['its_target_version']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_target_version']]) is False else '')
                    redmine_status = str(redmine_row[self.FIXED_KEYWORDS['its_status']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_status']]) is False else '')

                    # 更新パラメータ初期化
                    param_operation = ''
                    param_status = redmine_status
                    param_version = redmine_version

                    # 完了mantisは「終了」で更新
                    if redmine_status not in self._ITS_CLOSED_STATUS and mantis_status in self._BTS_CLOSED_STATUS:
                        param_operation = self.FIXED_KEYWORDS['its_operation_update']
                        param_status = self.FIXED_KEYWORDS['its_status_close']
                        param_version = mantis_version if mantis_version != '' else redmine_version
                    # 該当チケットとMantisのバージョンが相違する場合はMantisバージョンに更新
                    elif mantis_version != '' and redmine_version !=  mantis_version:
                        param_operation = self.FIXED_KEYWORDS['its_operation_update']
                        param_status = redmine_status
                        param_version = mantis_version

                    # 登録実行
                    if param_operation != '': 
                        # ROW追加
                        new_row.clear()
                        new_row.update({
                            self.FIXED_KEYWORDS['its_operation']:param_operation,
                            self.FIXED_KEYWORDS['its_id']:str(redmine_row[self.FIXED_KEYWORDS['its_id']]),
                            self.FIXED_KEYWORDS['its_tracker']:str(redmine_row[self.FIXED_KEYWORDS['its_tracker']]),
                            self.FIXED_KEYWORDS['its_parent_id']:str(redmine_row[self.FIXED_KEYWORDS['its_parent_id']]),
                            self.FIXED_KEYWORDS['its_status']:param_status,
                            self.FIXED_KEYWORDS['its_title']:str(redmine_row[self.FIXED_KEYWORDS['its_title']]),
                            self.FIXED_KEYWORDS['its_author']:'',
                            self.FIXED_KEYWORDS['its_assigned_to']:str(redmine_row[self.FIXED_KEYWORDS['its_assigned_to']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_assigned_to']]) is False else ''),
                            self.FIXED_KEYWORDS['its_update_date']:'',
                            self.FIXED_KEYWORDS['its_category']:'',
                            self.FIXED_KEYWORDS['its_target_version']:param_version,
                            self.FIXED_KEYWORDS['its_start_date']:str(redmine_row[self.FIXED_KEYWORDS['its_start_date']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_start_date']]) is False else ''),
                            self.FIXED_KEYWORDS['its_due_date']:str(redmine_row[self.FIXED_KEYWORDS['its_due_date']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_due_date']]) is False else ''),
                            self.FIXED_KEYWORDS['its_estimated_hours']:str(redmine_row[self.FIXED_KEYWORDS['its_estimated_hours']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_estimated_hours']]) is False else '0'),
                            self.FIXED_KEYWORDS['its_total_estimated_hours']:'',
                            self.FIXED_KEYWORDS['its_spent_hours']:str(redmine_row[self.FIXED_KEYWORDS['its_spent_hours']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_spent_hours']]) is False else '0'),
                            self.FIXED_KEYWORDS['its_total_spent_hours']:'',
                            self.FIXED_KEYWORDS['its_done_ratio']:str(redmine_row[self.FIXED_KEYWORDS['its_done_ratio']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_done_ratio']]) is False else '0'),
                            self.FIXED_KEYWORDS['its_created_on']:'',
                            self.FIXED_KEYWORDS['its_closed_on']:'',
                            self.FIXED_KEYWORDS['its_priority']:str(redmine_row[self.FIXED_KEYWORDS['its_priority']] if pd.isna(redmine_row[self.FIXED_KEYWORDS['its_priority']]) is False else '通常'),
                            self.FIXED_KEYWORDS['its_description']:mantis_url
                        })
                        output_new_rows.append(new_row.copy())

        # 出力DataFrame設定
        self._pd_its_entry = pd.DataFrame(output_new_rows, columns=self._ITS_ENTRY_COLUMNS)
    