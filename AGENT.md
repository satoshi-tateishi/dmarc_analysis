# Role: DMARC Analysis System Architect

## Project Overview

DMARCレポート(XML)を自動収集・解析し、可視化するためのセルフホスト型システムを構築する。 商用サービスを利用せず、OSSの `parsedmarc` スタックを Docker Compose で構成する。

現在の実装では、`.env` の値から `parsedmarc.ini` を起動時に生成し、`parsedmarc` は IMAP を常駐監視する。可視化は Grafana のプロビジョニングで自動設定し、送信元 IP の注釈は別ファイルで管理する。

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
4.  認証情報を Git 管理から分離しつつ、ローカルで再現可能な運用スクリプトを整備する。

## Constraints & Security

-   認証情報（IMAPパスワード等）は直接書き込まず `.env` ファイルで管理する。
-   ローカル開発環境から開始し、将来的に Linux サーバー（Ubuntu等）へのデプロイを想定する。
-   `parsedmarc.ini` の実体は Git 管理しない。`parsedmarc.ini.template` と `.env` から起動時生成する。
-   送信元 IP の注釈は `grafana/config/ip_annotations.json` で管理し、ダッシュボード JSON へ直接手編集しない。

## Current Implementation

-   `docker-compose.yml`
    -   `elasticsearch`, `grafana`, `parsedmarc`, `imap-cleanup` の4サービス構成
    -   ローカル向けのメモリ制限付き
-   `parsedmarc`
    -   `scripts/render_parsedmarc_ini.py` で `.env` から `parsedmarc.ini` を生成
    -   `parsedmarc.ini.template` を元に起動
    -   現在は `watch = True` で常駐監視
-   `grafana`
    -   `grafana/provisioning/datasources/datasource.yml`
    -   `grafana/provisioning/dashboards/dashboard-provider.yml`
    -   `grafana/dashboards/dmarc-overview.json`
    -   `DMARC分析` フォルダ配下に `DMARC 概要` ダッシュボードを表示
-   `imap-cleanup`
    -   `scripts/imap_cleanup.py`
    -   IMAP 上の `DMARC/Archive/*` 配下を保持日数で定期削除

## Operational Files

-   `.env`
    -   IMAP 接続情報、Grafana 管理者情報、Elasticsearch メモリ設定を保持
-   `.env.example`
    -   `.env` のテンプレート
-   `parsedmarc.ini.template`
    -   `parsedmarc` の設定テンプレート
-   `grafana/config/ip_annotations.json`
    -   既知の送信元 IP と注釈の一覧

## Operational Scripts

-   `scripts/render_parsedmarc_ini.py`
    -   `.env` の値を `parsedmarc.ini.template` に流し込む
-   `scripts/imap_cleanup.py`
    -   IMAP アーカイブフォルダの古いメールを削除する
-   `scripts/update_grafana_annotations.py`
    -   `grafana/config/ip_annotations.json` の内容を `grafana/dashboards/dmarc-overview.json` に反映する
-   `scripts/apply_ip_annotations.sh`
    -   注釈反映と Grafana 再起動を 1 コマンドで実行する

## Common Operations

-   起動
    -   `docker compose up -d`
-   停止
    -   `docker compose stop`
-   `parsedmarc` だけ止める
    -   `docker compose stop parsedmarc`
-   注釈反映
    -   `./scripts/apply_ip_annotations.sh`
-   Grafana
    -   URL: `http://localhost:3000`
-   Elasticsearch
    -   URL: `http://localhost:9200`

## Dashboard Notes

-   `主な送信元 IP`
    -   `送信元 IP`, `逆引きホスト名`, `件数` を表示
    -   既知 IP は `grafana/config/ip_annotations.json` から注釈を反映
-   `DMARC 判定結果`
    -   `判定 | 件数` の表で表示
    -   例: `成功 | 9`
-   Grafana 本体 UI の完全日本語化は行わない
    -   安全な範囲として、ダッシュボード名、フォルダ名、パネル名、凡例を日本語化する
