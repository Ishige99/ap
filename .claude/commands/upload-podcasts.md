Playwright MCP を使って `podcast/` ディレクトリの音声ファイル（m4a）を Spotify for Creators にアップロードしてください。

対象ポッドキャスト: https://creators.spotify.com/pod/show/1VQp6b0NPqZ10nVgtOohDH/episodes

## 前提条件

- Playwright MCP が設定済みであること（未設定なら `claude mcp add playwright --transport stdio -- npx -y @playwright/mcp@latest` で追加し、セッションを再起動）

## 手順

### 1. ログイン情報の準備

- `.env` ファイルを確認し、`SPOTIFY_EMAIL` と `SPOTIFY_PASSWORD` があればそのまま使用
- なければ `AskUserQuestion` でユーザーにメールアドレスとパスワードを質問し:
  - `.env` に書き込む
  - `.env.example` をテンプレートとして作成（プレースホルダー値）
  - `.gitignore` に `.env` を追加（まだなければ）

```
# .env の形式
SPOTIFY_EMAIL=actual-email@example.com
SPOTIFY_PASSWORD=actual-password

# .env.example の形式
SPOTIFY_EMAIL=your-email@example.com
SPOTIFY_PASSWORD=your-password
```

### 2. ブラウザ起動とログイン

1. Playwright MCP でブラウザを起動
2. https://creators.spotify.com にアクセス
3. `.env` のメールアドレスとパスワードでログインフォームに自動入力
4. ログイン完了後、https://creators.spotify.com/pod/show/1VQp6b0NPqZ10nVgtOohDH/episodes に移動

### 3. アップロード済みエピソードの確認

1. エピソード一覧ページのコンテンツを取得
2. 既存エピソードのタイトルリストを抽出
3. `podcast/` ディレクトリのファイル一覧と比較し、スキップ対象を特定

### 4. アップロード順序の検証

1. `podcast/` 配下の全 `.m4a` ファイルをエピソード番号順にソート（`#00a` → `#00b` → `#01` → `#02` → ...）
2. ソート済みリストで**連番の欠番をチェック**
   - 例: `#11` の次が `#13` なら、`#12` が欠番
   - 欠番が見つかった場合 → **処理を停止**し、欠番を報告してユーザーに確認
   - ユーザーが「スキップして続行」を指示すれば、その欠番を飛ばして続行

### 5. エピソードのアップロード

各ファイルについて順番に以下を実行:

1. アップロード済みリストにタイトルが含まれていれば → **スキップ**
2. 新規エピソード作成画面に移動
3. m4aファイルをアップロード（Playwright のファイル選択機能を使用）
4. **タイトル**: ファイル名から拡張子を除去（例: `#01_2進数と小数変換 ― コンピュータの数の扱い方`）
5. **詳細**: `project_docs/episode_prompts.md` からエピソード番号（`### #XX`）に対応するセクションの本文を入力
   - `#00a`, `#00b` は episode_prompts.md に対応エントリなし → 詳細は空またはタイトルのみ
6. 保存/公開

**注意**: Spotify for Creators の具体的なUI要素（ボタン位置、入力フィールドのセレクタ等）は、ブラウザを開いた後にアクセシビリティツリーで確認して決定すること。サイトのUIは変更される可能性があるため、事前に固定しない。

### 6. 検証

1. エピソード一覧ページで全エピソードが表示されることを確認
2. タイトルと詳細が正しく設定されていることをランダムに数件確認
