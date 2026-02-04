from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

class AbstractBts2Its(ABC):
    """BTSからITSへの変換抽象クラス
    """
    #
    # public定数
    #
    FIXED_KEYWORDS = {}                 # 固定キーワードマッピング
    #
    # protected変数
    #
    _pd_bts:pd.DataFrame = None         # BTSデータ
    _pd_its:pd.DataFrame = None         # ITSデータ
    _pd_its_entry: pd.DataFrame = None  # ITS起票データ
    #
    # protected定数
    #
    _BTS_DATA_COLUMNS = []              # BTSデータカラム
    _ITS_DATA_COLUMNS = []              # ITSデータカラム
    _ITS_ENTRY_COLUMNS = []             # ITS起票データカラム

    #
    # コンストラクタ/デストラクタ
    #
    def __init__(self) -> None:
        """コンストラクタ
        """
        self._pd_bts = pd.DataFrame(columns=self._BTS_DATA_COLUMNS) if len(self._BTS_DATA_COLUMNS) > 0 else pd.DataFrame()          # BTSデータ
        self._pd_its = pd.DataFrame(columns=self._ITS_DATA_COLUMNS) if len(self._ITS_DATA_COLUMNS) > 0 else pd.DataFrame()          # ITSデータ
        self._pd_its_entry = pd.DataFrame(columns=self._ITS_ENTRY_COLUMNS) if len(self._ITS_ENTRY_COLUMNS) > 0 else pd.DataFrame()  # ITS起票データ


    def __del__(self) -> None:
        """デストラクタ
        """
        pass

    #
    # publicメソッド
    #
    @abstractmethod
    def load_bts(self, file_path: Path) -> None:
        """バグ管理データ読み取り

        Args:
            file_path (Path): データのファイルパス
        """
        pass

    @abstractmethod
    def load_its(self, file_path: Path) -> None:
        """Issue管理データ読み取り

        Args:
            file_path (Path): データのファイルパス
        """
        pass

    @abstractmethod
    def bts_to_its(self) -> None:
        """BTSからITSへの起票データ作成
        """
        pass

    @abstractmethod
    def get_its_entry_data(self) -> pd.DataFrame:
        """ITSの起票データ取得

        Returns:
            pd.DataFrame: Pandas.DataFrame型
        """
        return self._pd_its_entry       # ITS起票データ