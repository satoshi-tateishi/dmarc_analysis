# DMARC Analysis

`parsedmarc`、Elasticsearch、Grafana を Docker Compose で構成した、DMARC レポートの収集・解析・可視化用プロジェクトです。

## 構成

- `parsedmarc`
  - IMAP で DMARC レポートメールを監視し、集計結果を Elasticsearch に保存
- `elasticsearch`
  - DMARC 集計データの保存先
- `grafana`
  - `DMARC分析 / DMARC 概要` ダッシュボードを自動表示
- `imap-cleanup`
  - IMAP アーカイブ配下の古いメールを定期削除

## セットアップ

1. `.env.example` を `.env` にコピー
2. `.env` に IMAP 接続情報、Grafana 管理者情報、必要ならメモリ設定を入力
3. コンテナ起動

```bash
docker compose up -d
```

## ローカル URL

- Grafana: `http://localhost:3000`
- Elasticsearch: `http://localhost:9200`

## 認証情報の扱い

- `.env` は Git に commit しない
- `parsedmarc` の設定実体は commit せず、`.env` と `parsedmarc.ini.template` から起動時生成する

## 主要ファイル

- [docker-compose.yml](/Users/satoshi/DMARC_Analysis/docker-compose.yml)
- [parsedmarc.ini.template](/Users/satoshi/DMARC_Analysis/parsedmarc.ini.template)
- [.env.example](/Users/satoshi/DMARC_Analysis/.env.example)
- [grafana/dashboards/dmarc-overview.json](/Users/satoshi/DMARC_Analysis/grafana/dashboards/dmarc-overview.json)
- [grafana/config/ip_annotations.json](/Users/satoshi/DMARC_Analysis/grafana/config/ip_annotations.json)

## ダッシュボード

Grafana には `DMARC分析` フォルダ配下に `DMARC 概要` ダッシュボードをプロビジョニングしています。

主な表示内容:

- `DMARC メール件数の推移`
- `DMARC 判定結果`
- `主な送信元 IP`
- `主なレポート送信元組織`

`主な送信元 IP` では次を表示します。

- 送信元 IP
- 逆引きホスト名
- 件数

## 送信元 IP 注釈

既知の IP に対する注釈は [grafana/config/ip_annotations.json](/Users/satoshi/DMARC_Analysis/grafana/config/ip_annotations.json) で管理します。

例:

```json
{
  "source_ip_annotations": {
    "112.78.125.20": "さくらインターネット"
  }
}
```

編集後は以下で反映します。

```bash
./scripts/apply_ip_annotations.sh
```

このスクリプトは次をまとめて実行します。

- `ip_annotations.json` をダッシュボードへ反映
- Grafana を再起動

## 主要スクリプト

- [scripts/render_parsedmarc_ini.py](/Users/satoshi/DMARC_Analysis/scripts/render_parsedmarc_ini.py)
  - `.env` の値から `parsedmarc.ini` を生成
- [scripts/imap_cleanup.py](/Users/satoshi/DMARC_Analysis/scripts/imap_cleanup.py)
  - IMAP アーカイブを保持日数で削除
- [scripts/update_grafana_annotations.py](/Users/satoshi/DMARC_Analysis/scripts/update_grafana_annotations.py)
  - 注釈一覧をダッシュボード JSON に反映
- [scripts/apply_ip_annotations.sh](/Users/satoshi/DMARC_Analysis/scripts/apply_ip_annotations.sh)
  - 注釈反映と Grafana 再起動をまとめて実行

## 日常運用

起動:

```bash
docker compose up -d
```

停止:

```bash
docker compose stop
```

`parsedmarc` だけ停止:

```bash
docker compose stop parsedmarc
```

Grafana 再起動:

```bash
docker compose restart grafana
```

## 補足

- Grafana 本体 UI の完全日本語化はしていません
- 安全な範囲として、ダッシュボード名、フォルダ名、パネル名、注釈を日本語化しています
