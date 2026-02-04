from bts2its.adaptors import BaseConverterAdaptor
from bts2its.common import *
from bts2its.mantis2redmine import DefaultMantis2Redmine
from bts2its.redmine_accessor import DefaultRedmineAccessor

class DefaultConverterAdaptor(BaseConverterAdaptor):
    """BTSからITSへの変換アダプター
    デフォルトの具象化クラス
    """
    #
    # コンストラクタ/デストラクタ
    #
    def __init__(self, project_name: str, bts_prefix: str) -> None:
        """コンストラクタ

        Args:
            project_name (str): プロジェクト名
            bts_prefix (str): BTSをフィルタするためのプレフィックス
        """
        # スーパークラスのコンストラクタ呼び出し
        super().__init__(project_name)
        
        # MantisBTからRedmineへの変換オブジェクト生成
        params = Mantis2RedmineParameters(
            project_name=project_name,
            bts_prefix=bts_prefix,
            bts_base_url=self._config.bts_url(),
            date_range=self._config.conversion_date_range(),
        )
        self._bts2its = DefaultMantis2Redmine(parameters=params)

        # Redmineアクセスオブジェクト生成
        self._its_accessor = DefaultRedmineAccessor(project_name=project_name, url=self._config.its_url(), key_string=self._config.its_api_key())
