import os
import pathlib
import yaml
from typing import Any, Dict

class Config:
    """設定情報管理クラス
    """
    #
    # Constructor / Destructor
    #
    def __init__(self) -> None:
        """コンストラクタ
        """
        # ベースパスの初期化
        self._base_path = pathlib.Path.cwd()
        # 環境変数からDocker環境フラグの初期化
        self._is_docker = os.getenv('IS_DOCKER', 'false').lower() == 'true'
        # settings.yamlファイルパスの初期化
        if self._is_docker:
            # ローカル環境のssettings.yamlパスを優先的に使用する
            self._settings_file = pathlib.Path("/data/settings.yaml")
            if not os.path.exists(self._settings_file):
                # ローカル環境にsettings.yamlが存在しない場合はコンテナ内の設定を使用する
                self._settings_file = pathlib.Path("/app/settings.yaml")
        else:
            self._settings_file = self._base_path / "settings.yaml"
        # 設定データの読み込み
        self._config_data = self._load_settings()

    def __del__(self) -> None:
        """デストラクタ
        """
        pass

    #
    # public methods
    #
    def get(self, key: str, default=None):
        """設定値の取得

        Args:
            key (str): 設定キー
            default: デフォルト値（キーが存在しない場合に返される値）
        Returns:
            設定値またはデフォルト値
        """
        return self._config_data.get(key, default)
    
    def adaptor_type_name(self) -> str:
        """Adapterの型名の取得

        Returns:
            str: Adapterの型名
        """
        adaptor_type_name = self._config_data.get("adapter_type_name", "")
        return adaptor_type_name
    
    def bts_url(self) -> str:
        """BTSのURLの取得

        Returns:
            str: BTSのURL
        """
        bts_settings = self._config_data.get("bts_settings", {})
        bts_url = bts_settings.get("url", "")
        return bts_url
    
    def bts_input_file(self) -> str:
        """BTSの入力ファイル名の取得

        Returns:
            str: BTSの入力ファイル名
        """
        bts_settings = self._config_data.get("bts_settings", {})
        bts_input_file = bts_settings.get("input_file", "")
        return bts_input_file

    def its_url(self) -> str:
        """ITSのURLの取得

        Returns:
            str: ITSのURL
        """
        its_settings = self._config_data.get("its_settings", {})
        its_url = its_settings.get("url", "")
        return its_url
    
    def its_api_key(self) -> str:
        """ITSのAPIキーの取得

        Returns:
            str: ITSのAPIキー
        """
        its_settings = self._config_data.get("its_settings", {})
        its_api_key = its_settings.get("api_key", "")
        return its_api_key
    
    def its_input_file(self) -> str:
        """ITSの入力ファイル名の取得

        Returns:
            str: ITSの入力ファイル名
        """
        its_settings = self._config_data.get("its_settings", {})
        its_input_file = its_settings.get("input_file", "")
        return its_input_file

    def conversion_output_file(self) -> str:
        """変換後の出力ファイル名の取得

        Returns:
            str: 変換後の出力ファイル名
        """
        conversion_settings = self._config_data.get("conversion_settings", {})
        output_file = conversion_settings.get("output_file", "")
        return output_file
    
    def conversion_date_range(self) -> int:
        """変換対象の期間（日数）の取得

        Returns:
            int: 変換対象の期間（日数）
        """
        conversion_settings = self._config_data.get("conversion_settings", {})
        date_range = conversion_settings.get("date_range", -1)
        return int(date_range)

    def input_path(self) -> str:
        """入力パスの取得
        Returns:
            str: 入力パス
        """
        path_settings = self._config_data.get("path_settings", {})
        temp_path = path_settings.get("input_path", "")
        if self._is_docker:
            return str(pathlib.Path('/data') / temp_path)
        else:
            # ローカル環境の場合はベースパスを考慮する
            return str(self._base_path / temp_path)
    
    def output_path(self) -> str:
        """出力パスの取得

        Returns:
            str: 出力パス
        """
        path_settings = self._config_data.get("path_settings", {})
        temp_path = path_settings.get("output_path", "")
        if not temp_path:
            return temp_path
        
        if self._is_docker:
            # Docker環境の場合はそのまま返す
            return str(pathlib.Path('/data') / temp_path)
        else:
            # ローカル環境の場合はベースパスを考慮する
            temp_abs_path = self._base_path / temp_path
            if not os.path.exists(temp_abs_path):
                # 絶対パスが存在しない場合は作成する
                os.makedirs(temp_abs_path, exist_ok=True)
            # 絶対パスを返す
            return str(temp_abs_path)

    #
    # protected methods
    #
    def _load_settings(self) -> Dict[str, Any]:
        """settings.yamlファイルの読み込み

        Returns:
            Dict[str, Any]: settings.yamlの内容を格納した辞書。settings.yamlが存在しない場合はデフォルト設定を返す。
        """
        # 一時的な辞書オブジェクトの作成
        temp_dict : Dict[str, Any] = {}
        # settings.yamlファイルの存在チェック
        if not os.path.exists(self._settings_file):
            # ファイルがない場合はデフォルト設定を返す
            temp_dict = {
                "adapter_type_name": "",
                "path_settings": {
                    "input_path": "input",
                    "output_path": "output",
                },
                "bts_settings": {
                    "url": "",
                    "input_file": "bts.csv",
                },
                "its_settings": {
                    "url": "",
                    "api_key": "",
                    "input_file": "its.csv",
                },
                "conversion_settings": {
                    "output_file": "output.csv",
                    "date_range": -1,
                },
            }
        else:
            # settings.yamlファイルの読み込み
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                temp_dict = yaml.safe_load(f)
        # 辞書オブジェクトを返す
        return temp_dict