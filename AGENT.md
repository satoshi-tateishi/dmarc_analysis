# Role: DMARC Analysis System Architect

## Project Overview

DMARCレポート(XML)を自動収集・解析し、可視化するためのセルフホスト型システムを構築する。 商用サービスを利用せず、OSSの `parsedmarc` スタックを Docker Compose で構成する。

## Technology Stack

-   **Analysis Engine:** parsedmarc (Python-based OSS)
-   **Database:** Elasticsearch (Storage for report data)
-   **Visualization:** Grafana (Dashboard)
-   **Environment:** Docker / Docker Compose
-   **Data Source:** IMAP (Fetching reports from a dedicated email account)

## Project Goals

1.  `docker-compose.yml` による一括起動環境の構築。
2.  さくらインターネット等のメールサーバーからIMAP経由でZIP/XMLを取得する設定。
3.  Grafana で Pass/Fail 率や送信元IPを可視化するダッシュボードの自動生成。

## Constraints & Security

-   認証情報（IMAPパスワード等）は直接書き込まず `.env` ファイルで管理する。
-   ローカル開発環境から開始し、将来的に Linux サーバー（Ubuntu等）へのデプロイを想定する。

