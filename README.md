# Wake-on-LAN Web App

Wake-on-LAN のマジックパケットを送信するシンプルな Web アプリです。モバイルフレンドリーな UI で送信先を指定でき、送信結果とログを画面上で確認できます。

## 特長

- 単一コンテナで動作 (docker-compose 不要)
- ベースイメージは `python:3.11-slim`
- ポートは `8200`
- モバイルフレンドリーな Web UI
- 環境変数ファイルでデフォルト送信先を設定可能
- 送信ログを UI 上で確認可能

## 必要要件

- Docker

## 環境変数

`.env.example` を参考に `.env` を用意してください。`.env` は `.gitignore` で管理対象外にしています。

| 変数 | 説明 | 例 |
| --- | --- | --- |
| `DEFAULT_MAC` | デフォルトの MAC アドレス | `00:11:22:33:44:55` |
| `DEFAULT_BROADCAST` | ブロードキャスト IP | `255.255.255.255` |
| `DEFAULT_PORT` | 送信ポート | `9` |
| `LOG_LIMIT` | UI に表示するログ件数 | `50` |

## 起動方法

```bash
# .env を用意
cp .env.example .env

# Docker イメージをビルド
docker build -t wol-app .

# コンテナを起動
docker run --rm -p 8200:8200 --env-file .env wol-app
```

Windows の場合は `run.bat` を実行すると同じ手順で起動できます。

ブラウザで `http://localhost:8200` にアクセスしてください。

## Linux環境でのイメージビルド手順

```bash
# 作業ディレクトリへ移動
cd /path/to/wol-app

# .env を用意 (必要に応じて編集)
cp .env.example .env

# Linux環境でDockerイメージをビルド
docker build -t wol-app:latest .
```

## 使い方

1. MAC アドレス、ブロードキャスト IP、ポートを入力します。
2. **送信** ボタンを押すとマジックパケットが送信されます。
3. 送信結果は「送信ログ」セクションに記録されます。

## 開発メモ

- `app.py` がアプリ本体です。
- UI は `templates/index.html` にあります。
