# バッチ実行関数
function Invoke-Batch {
    param (
        [string]$project,
        [string]$prefix = ""
    )
    
    $fullCurrentPath = Get-Location
    $fullCustomizePath = Join-Path $fullCurrentPath "customizes"

    docker run -it --rm `
        -v "$($fullCurrentPath):/data" `
        -v "$($fullCustomizePath):/app/src/bts2its/customizes" `
        ghcr.io/bteam-toku/bts2its:latest $project --prefix=$prefix --skip_its_entry # ITS登録する場合は --skip_its_entry を外す
}

# 一つ上の親ディレクトリをカレントフォルダリに設定（環境に合わせて変更してください）
Set-Location -Path (Join-Path $PSScriptRoot "..")

# # x0000プロジェクトの実行
# Invoke-Batch -project "x0000_develop" -prefix "x0000"