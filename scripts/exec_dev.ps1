# バッチ実行関数
function Invoke-Batch {
    param (
        [string]$project,
        [string]$prefix = ""
    )
    uv run execute $project --prefix=$prefix --skip_its_entry  # ITS登録する場合は --skip_its_entry を外す
}

# 一つ上の親ディレクトリをカレントフォルダリに設定（環境に合わせて変更してください）
Set-Location -Path (Join-Path $PSScriptRoot "..")
.\scripts\env.ps1

# # x0000プロジェクトの実行
# Invoke-Batch -project "x0000_develop" -prefix "x0000"
