from bts2its.factories import Factory
from bts2its import Config
from pathlib import Path
import sys
import argparse

def main():
    """メイン処理
    """
    # argument取得
    parser = argparse.ArgumentParser()
    parser.add_argument('project', type=str, default='', help='redmineのプロジェクト名')
    parser.add_argument('--input_path', type=str, default='', help='入力元のフォルダパス。(デフォルトは設定ファイルのあるフォルダ内のinputフォルダ)')
    parser.add_argument('--output_path', type=str, default='', help='出力先のフォルダパス。(デフォルトは設定ファイルのあるフォルダ内のoutputフォルダ)')
    parser.add_argument('--prefix', type=str, default='', help='BTSをバージョンでフィルタするための文字列。（デフォルト:フィルタなし）')
    parser.add_argument('--skip_its_entry', action='store_true', help='ITSに起票するかどうかのフラグ。（デフォルト:起票する）')
    args = parser.parse_args()
    # config取得
    config = Config()
    # プロジェクト名チェック
    if args.project == '':
        print('project name missing error.')
        sys.exit()

    # 入力パス情報取得
    input_path = Path(args.input_path if args.input_path != '' else config.input_path())
    input_path = input_path.resolve()
    bts_file_path = input_path / args.project / config.bts_input_file()
    its_file_path = input_path / args.project / config.its_input_file()
    # 入力ファイルが存在しなければ終了
    if bts_file_path.is_file() is False or its_file_path.is_file() is False:
        print(f'input file missing error. {bts_file_path} or {its_file_path}')
        sys.exit()

    # BTSのパラメータチェック
    if config.bts_url() == '':
        print('BTS URL missing error.')
        sys.exit()
    # ITSのパラメータチェック
    if config.its_url() == '' or config.its_api_key() == '':
        print('ITS URL or API-KEY missing error.')
        sys.exit()

    # 出力パス情報取得
    output_path = Path(args.output_path if args.output_path != '' else config.output_path())
    output_path = output_path.resolve()
    # 出力パスが存在しなければ作成
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Factory経由でBTS->ITSアダプター生成
    factory = Factory()
    converter = factory.create(project_name=args.project, bts_prefix=args.prefix, adaptor_type_name=config.adaptor_type_name())

    # BTSからITSへの変換処理実行
    converter.convert(bts_data_path=bts_file_path, its_data_path=its_file_path)

    # ITSに起票データ登録
    if not args.skip_its_entry:
        converter.entry_its()
    else:
        print('ITS entry process is skipped.')

    # 出力CSVファイル名取得
    output_file_path = output_path / args.project / config.conversion_output_file()
    converter.save_csv(file_path=output_file_path)

if __name__ == "__main__":
    main()