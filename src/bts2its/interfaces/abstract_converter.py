from abc import ABC, abstractmethod
from bts2its.interfaces.abstract_bts2its import AbstractBts2Its
from its_accessor import AbstractItsAccessor
from pathlib import Path

class AbstractConverter(ABC):
    """BTSからITSへの変換抽象クラス
    """
    #
    # protected変数
    #
    _bts2its: AbstractBts2Its  = None           # BTSからITSへの変換オブジェクト
    _its_accessor: AbstractItsAccessor = None   # ITSアクセスオブジェクト

    #
    # コンストラクタ/デストラクタ
    #
    def __init__(self) -> None:
        """コンストラクタ
        """
        pass

    def __del__(self) -> None:
        """デストラクタ
        """
        pass

    #
    # publicメソッド
    #
    @abstractmethod
    def convert(self, bts_data_path: Path, its_data_path: Path) -> None:
        """BTSからITSへの変換

        Args:
            bts_data_path (Path): BTSデータファイルパス
            its_data_path (Path): ITSデータファイルパス
        """
        pass

    @abstractmethod
    def entry_its(self) -> None:
        """ITSへの起票データ登録
        """
        pass

    @abstractmethod
    def save_csv(self, file_path: Path) -> None:
        """CSVファイル保存

        Args:
            file_path (Path): 保存ファイルパス
        """
        pass