# trello-asakai

## セットアップ

- Trelloにボードを作成する。
- ボードに"PENDING" "TODO" "WIP" "IN REVIEW" "DONE" "CLOSED" 6つのリストを作成する
- TrelloのAPIキーを入手する。(https://trello.com/app-key)
- SlackのIncoming Webhookを設定する
- 環境変数を設定する
```
TRELLO_API_KEY: TrelloのAPI KEY
TRELLO_API_SECRET: TrelloのAPI Secret
TRELLO_BOARD: Trelloのボード名
SLACK_WEBHOOK_URL: SlackのIncoming Webhook URL
```

## 使い方

### Trelloのラベル

Slackに次のようなものをながしたいとき

```
# WIP
[営業] ●●社 クローズ
  - [x] 契約書作成
ファイル: https://dropbox...
  - [ ] 契約書送付
  - [ ] 契約書受領
```

- `[営業] ` はトピック
- "●●社 クローズ" がタスク名
- "契約書作成" などがサブタスク名
- "ファイル: https://dropbox..." が補足
 
- `!ラベル名` というふうに、ラベル名の最初に `!` をつけるとトピックになります。なかった場合 `Other` になります。
- カードのタイトルがタスク名になります。
- カードにチェックリストを作成すると、それがサブタスクになります。各項目がサブタスク名になります。チェックも反映されます。（チェックリストは複数作らない、1つしか対応していない）
- `!サブタスク名` を先頭行にしたコメントをつけると、そのサブタスクに対する補足になります。

```
!契約書作成
ファイル: https://dropbox...
```
というコメントをカードにつけてください。