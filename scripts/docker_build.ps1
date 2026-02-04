# 一つ上の親ディレクトリをカレントフォルダリに設定（環境に合わせて変更してください）
Set-Location -Path (Join-Path $PSScriptRoot "..")
# Dockerイメージのビルド
docker build --no-cache -t ghcr.io/bteam-toku/bts2its:latest .