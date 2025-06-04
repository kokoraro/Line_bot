# LINE Bot プロジェクト

この LINE Bot は、ユーザーのメッセージに応じて以下の機能を提供します：

- Ping 応答（“ping” → “pong”）
- 物件に関する問い合わせフロー（物件→エリア→予算）
- 目的リンク案内（キーワードマッチ）
- FAQ 自動応答（CSVで管理）
- OpenAI GPT による汎用チャット応答
- Google Sheets への会話ログ出力

FastAPI による Webhook サーバーとして構成されており、Vercel へのデプロイに対応しています。

---

# ファイル構成

## linebot_fastapi_bot_v3/
- **index.py**：エントリーポイント。Webhook ハンドラーやルーティングを含む
- **api/faq.py**：FAQ 応答機能（CSV 検索ベース）
- **api/goal_redirect.py**：目的リンク返信機能（CSV 検索ベース）
- **api/openai_chat.py**：GPT 応答生成ロジック
- **api/logger.py**：Google Sheets への会話ログ出力
- **config.json**：デフォルト応答などの設定ファイル
- **.env**：環境変数（ローカル開発用）
- **README.md**：プロジェクト概要（本ファイル）

---

# 使用技術

- **Python 3.13**
- **FastAPI**
- **LINE Messaging API SDK v3**
- **gspread / Google API**
- **OpenAI API**
- **dotenv**（環境変数管理）
- **Vercel**（サーバーレスデプロイ）

---

# 機能仕様

## 1. Ping–Pong 機能

- ユーザーが「ping」と送信 → Bot は「pong」と返信します

## 2. Webhook 受信処理

- エンドポイント：`POST /api/callback`
- `X-Line-Signature` を検証
- メッセージ処理の順序：
  1. **目的リンク**：`goal.csv` に登録されたキーワードをマッチし、対応する URL を返信
  2. **FAQ応答**：`faq.csv` に一致する質問があれば回答を返信
  3. **物件問い合わせフロー**：
     - 「物件」→ エリア（都道府県・区市）を質問
     - エリアが来たら予算を質問
     - 予算が来たら完了メッセージを返す
  4. **GPT 応答**：OpenAI API による自然な会話応答を生成
- `dummy-reply-token` を受信した場合はログ出力のみ（テスト用）

## 3. Google Sheets ログ出力

- `.env` に `SERVICE_ACCOUNT_JSON` を登録（JSON を1行文字列化）
- 会話のタイムスタンプ・ユーザーID・ユーザーメッセージ・Bot応答を記録
- API：`gspread` / Google Sheets API v4 使用

## 4. エラー処理

- Webhook 全体に対して `ExceptionHandler` によるグローバル例外処理を実装
- ステータスコード `500` で JSON の `{"error": "...内容..."}` を返却

---


