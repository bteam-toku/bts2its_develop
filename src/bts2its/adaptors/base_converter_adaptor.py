from bts2its.interfaces import AbstractConverter
from bts2its.common import *
from bts2its.config import Config
from pathlib import Path

class BaseConverterAdaptor(AbstractConverter):
    """BTSからITSへの変換アダプター
    デフォルトの具象化クラス
    """
    #
    # protected変数
    #
    _project_name: str = ""                         # プロジェクト名
    _config: Config = None                          # 設定オブジェクト

    #
    # コンストラクタ/デストラクタ
    #
    def __init__(self, project_name: str) -> None:
        """コンストラクタ

        Args:
            project_name (str): プロジェクト名
        """
        # スーパークラスのコンストラクタ呼び出し
        super().__init__()
        # プロジェクト名設定
        self._project_name = project_name
        # configオブジェクト取得
        self._config = Config()        

    def __del__(self) -> None:
        """デストラクタ
        """
        pass

    #
    # publicメソッド
    #
    def convert(self, bts_data_path: Path, its_data_path: Path) -> None:
        """BTSからITSへの変換

        Args:
            bts_data_path (Path): BTSデータファイルパス
            its_data_path (Path): ITSデータファイルパス
        """
        # ファイル存在チェック
        if not bts_data_path.is_file() or not its_data_path.is_file():
            raise FileNotFoundError(f'BTS data file not found: {bts_data_path} or ITS data file not found: {its_data_path}')
        
        # BTSデータとITSデータの読み込み
        self._bts2its.load_bts(str(bts_data_path))
        self._bts2its.load_its(str(its_data_path))

        # BTSからITSへの変換
        self._bts2its.bts_to_its()

    def entry_its(self) -> None:
        """ITSへの起票データ登録
        """
        # プロジェクト情報読み込み
        if self._its_accessor.load_project() is False:
            print('ITS project load error.')
            return

        # ITS起票データ取得        
        pd_its_entry = self._bts2its.get_its_entry_data()
        issue_data = self._its_accessor.its_payload_template.copy()

        # BTS->ITSに起票・更新
        for _, row in pd_its_entry.iterrows():
            # 行データ辞書化
            row_data = row.to_dict()
            # 行の操作種別とITS ID取得
            operation = row_data.get(self._bts2its.FIXED_KEYWORDS['its_operation'], '')
            issue_id = row_data.get(self._bts2its.FIXED_KEYWORDS['its_id'], '')
            # 操作種別が空の場合はスキップ
            if operation is None or operation == '':
                continue
            # 更新データ作成
            dict_keys = set(issue_data.keys()) & set(row_data.keys())
            for key in dict_keys:
                issue_data[key] = row_data[key]
            # 新規起票（IDの指定がない場合）
            if issue_id == '' or issue_id is None:
                self._its_accessor.create_issue(issue_data)
            # 既存起票更新（IDの指定がある場合）
            else:
                update_data = self._its_accessor.load_issue(issue_id)
                self._its_accessor.update_issue(update_data, issue_data)

    def save_csv(self, file_path: Path) -> None:
        """CSVファイル保存

        Args:
            file_path (Path): 保存ファイルパス
        """
        # ITS起票データの取得
        pd_its_entry = self._bts2its.get_its_entry_data()
        # CSVファイル保存
        if not file_path.parent.exists():
            # 親ディレクトリが存在しない場合は作成する
            file_path.parent.mkdir(parents=True, exist_ok=True)
        pd_its_entry.to_csv(file_path, index=False, encoding='utf-8-sig')
