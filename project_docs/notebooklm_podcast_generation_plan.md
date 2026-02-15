# NotebookLM Enterprise API 音声概要自動生成 - 実装計画

## 概要

応用情報技術者試験の学習プロジェクト。`episode_list.md` に定義された117エピソードの音声教材を NotebookLM Enterprise API 経由で自動生成する。

---

## 前提条件

- NotebookLM Enterprise を Web UI で使用中（全体用ノートブック1つ）
- API は v1alpha（`discoveryengine.googleapis.com`）
- ノートブックごとに音声概要は1つのみ → エピソードごとにノートブックを作成する必要がある
- ソースには `textContent` 形式でテキストを直接投入可能

## 依存パッケージ

- `requests` — HTTP 通信
- `google-auth` — GCP 認証トークン取得

---

## Step 1: GCP セットアップ手順書（`SETUP_GCP.md` 新規作成）

Web UI で使用中の NotebookLM Enterprise に対して API アクセスを設定する手順書を作成する。

### 記載内容

1. **GCP プロジェクトの確認**
   - 既存の Workspace に紐づくプロジェクト ID の確認方法
   - `gcloud projects list` で確認

2. **Discovery Engine API の有効化**
   ```
   gcloud services enable discoveryengine.googleapis.com
   ```

3. **IAM ロール付与**
   - `Cloud NotebookLM User`（API 利用者向け）
   - `ディスカバリーエンジン管理者`（管理用）

4. **認証設定**
   ```
   gcloud auth login
   gcloud auth application-default login
   gcloud auth print-access-token  # 動作確認
   ```

5. **環境変数設定**
   ```
   export GOOGLE_CLOUD_PROJECT=your-project-id
   ```

6. **動作確認コマンド**
   - curl で notebooks 一覧取得して疎通確認

---

## Step 2: `generate_podcasts.py` 新規作成

### 2.1 データ解析モジュール

#### `parse_episode_list(path)` — episode_list.md の解析

`episode_list.md` のフォーマット:
```
## テクノロジ系           ← field（分野）
### 基礎理論             ← category（カテゴリ）
#### #01 タイトル ― サブタイトル  ← episode
- トピック名             ← topic
```

返却する構造体（エピソードごとの dict のリスト）:
```python
{
    "number": 1,                          # エピソード番号
    "title": "2進数と小数変換",             # メインタイトル
    "subtitle": "コンピュータの数の扱い方",   # サブタイトル（―の後）
    "full_title": "2進数と小数変換 ― コンピュータの数の扱い方",
    "field": "テクノロジ系",                # 分野
    "category": "基礎理論",                # カテゴリ
    "topics": ["2進数小数変換", "基数変換"]  # トピック一覧
}
```

パース手順:
1. `## ` で始まる行 → `field` を更新
2. `### ` で始まる行 → `category` を更新
3. `#### #` で始まる行 → 新エピソード開始。正規表現 `#### #(\d+)\s+(.+?)(?:\s+―\s+(.+))?$` で番号・タイトル・サブタイトルを抽出
4. `- ` で始まる行 → 現在のエピソードの topics に追加
5. `---` や空行はスキップ

#### `parse_category_taxonomy(path)` — category_taxonomy.md の解析

`category_taxonomy.md` のフォーマット:
```
## テクノロジ系 (T)       ← field
### 基礎理論             ← category
#### 数値表現・計算       ← subcategory
- 2進数小数変換          ← topic
```

返却: トピック名 → カテゴリ階層のマッピング dict
```python
{
    "2進数小数変換": {
        "field": "テクノロジ系",
        "category": "基礎理論",
        "subcategory": "数値表現・計算"
    },
    ...
}
```

パース手順:
1. `## ` で始まる行 → `field` 更新（`(T)` 等の括弧部分は除去）
2. `### ` で始まる行 → `category` 更新
3. `#### ` で始まる行 → `subcategory` 更新
4. `- ` で始まる行 → トピック名をキーにして dict に登録

#### `load_questions(path)` — ap_questions_1000.json の読み込み

JSON の構造（各問題）:
```json
{
    "id": "2010h22a_q05",
    "exam_name": "平成22年度秋期",
    "question_number": 5,
    "field": "T",
    "category": "アルゴリズムとプログラミング",
    "subcategory": "データ構造",
    "question_text": "...",
    "choices": {"ア": "...", "イ": "...", "ウ": "...", "エ": "..."},
    "correct_answer": "エ",
    "explanation": "..."
}
```

返却: `questions["questions"]` リストをそのまま読み込み

#### `find_related_questions(questions, episode)` — 関連過去問の検索

マッチングロジック:
1. **カテゴリ一致**: 問題の `category` がエピソードの `category` と一致
2. **トピック一致**: 問題の `subcategory` またはテキスト内にエピソードの `topics` のいずれかが含まれる
3. 優先度: トピック完全一致 > subcategory 一致 > category 一致
4. 最大取得件数: 1エピソードあたり **最大10問**（多すぎるとソースが冗長になる）
5. `quality_score` が高い問題を優先

### 2.2 コンテンツ生成モジュール

#### `build_source_content(episode, taxonomy, questions)` — ソーステキスト構築

生成するテキストの構造:
```
# 応用情報技術者試験 解説教材

## テーマ: {title} ― {subtitle}

### 分野構造
{field} > {category} > {subcategory}

### 関連トピック
- {topic1}
- {topic2}
...

### 各トピックの解説ポイント
（トピックごとの subcategory 情報をもとに、分類上の位置づけを記述）

### 関連過去問

【問題1】({exam_name} 問{question_number})
{question_text}
ア {choice_a}  イ {choice_b}  ウ {choice_c}  エ {choice_d}
正解: {correct_answer}
解説: {explanation}

【問題2】...
（最大10問）
```

注意点:
- `question_text` に画像参照が含まれる問題（OCR 品質が低い `quality_score < 0.8` のもの）はスキップ
- テキスト全体が長すぎる場合（50,000文字超）は過去問数を削減

### 2.3 NotebookLM API クライアント

#### API エンドポイント

ベース URL:
```
https://discoveryengine.googleapis.com/v1alpha/projects/{project}/locations/{location}/notebookLmApps
```

#### 認証

```python
import google.auth
import google.auth.transport.requests

credentials, project = google.auth.default()
credentials.refresh(google.auth.transport.requests.Request())
headers = {"Authorization": f"Bearer {credentials.token}"}
```

#### `create_notebook(title)` — ノートブック作成

```
POST /v1alpha/projects/{project}/locations/{location}/notebookLmApps/{app}/notebooks
Content-Type: application/json

{"title": "AP解説 #01 2進数と小数変換"}
```

レスポンスから `notebook_name`（リソース名）を取得。

#### `add_sources(notebook_name, text_content)` — ソース追加

```
POST /v1alpha/projects/{project}/locations/{location}/notebookLmApps/{app}/notebooks/{notebook}/sources:batchCreate
Content-Type: application/json

{
  "requests": [{
    "source": {
      "textContent": {
        "content": "..."
      },
      "displayName": "AP解説 #01 教材テキスト"
    }
  }]
}
```

#### `generate_audio(notebook_name, episode)` — 音声概要生成

```
POST /v1alpha/projects/{project}/locations/{location}/notebookLmApps/{app}/notebooks/{notebook}/audioOverviews:generate
Content-Type: application/json

{
  "episodeFocus": "{title}について深掘りしながら、応用情報技術者試験の頻出ポイントをわかりやすく解説してください。過去問の解き方のコツも紹介してください。",
  "languageCode": "ja"
}
```

レスポンスは Long Running Operation（LRO）。`operation_name` を取得。

#### `poll_operation(operation_name)` — 完了待機（ポーリング）

```
GET /v1alpha/{operation_name}
```

ポーリング戦略:
- 初回待機: 30秒
- ポーリング間隔: 15秒
- 最大待機時間: 15分（タイムアウト）
- `done: true` になったら完了

#### `download_audio(notebook_name, output_path)` — MP3 ダウンロード

```
GET /v1alpha/projects/{project}/locations/{location}/notebookLmApps/{app}/notebooks/{notebook}/audioOverviews
```

レスポンスの `audioOverview.audioUri` から MP3 をダウンロード。

保存先: `podcasts/ep{NNN}_{sanitized_title}.mp3`
- NNN: 3桁ゼロ埋め（001〜117）
- sanitized_title: タイトルからファイル名に使えない文字を除去

### 2.4 メイン処理フロー

```
1. 引数パース（argparse）
2. episode_list.md 解析 → 全117エピソード取得
3. category_taxonomy.md 解析 → トピック→カテゴリ階層マッピング
4. ap_questions_1000.json 読込 → 過去問リスト
5. 対象エピソードをフィルタリング（--episode / --range / --all）
6. podcasts/ ディレクトリ作成（なければ）
7. 対象エピソードごとにループ:
   a. 既存 MP3 チェック → 存在すればスキップ（再開対応）
   b. 関連過去問検索
   c. ソーステキスト構築
   d. --dry-run なら内容を表示して次へ
   e. ノートブック作成
   f. ソース追加
   g. 音声概要生成リクエスト
   h. ポーリングで完了待機
   i. MP3 ダウンロード
   j. 進捗ログ出力（「エピソード 3/117 生成完了」）
8. 完了サマリ出力
```

### 2.5 CLI 引数

| 引数 | 説明 | 例 |
|---|---|---|
| `--episode N` | 指定エピソードのみ生成 | `--episode 1` |
| `--range N-M` | 範囲指定 | `--range 1-10` |
| `--all` | 全117エピソード | `--all` |
| `--dry-run` | API 呼び出しなし（コンテンツのみ表示） | `--dry-run` |
| `--project ID` | GCP プロジェクト ID | `--project my-project` |
| `--location LOC` | リージョン（デフォルト: `global`） | `--location us` |
| `--output-dir DIR` | 出力ディレクトリ（デフォルト: `podcasts`） | `--output-dir out` |

`--episode`, `--range`, `--all` のいずれか1つが必須。

### 2.6 エラーハンドリング

| エラー種別 | 対処 |
|---|---|
| API 呼び出し失敗（5xx） | 指数バックオフでリトライ（最大3回、初回2秒） |
| API 呼び出し失敗（4xx） | エラーメッセージを表示してそのエピソードをスキップ |
| 認証エラー（401/403） | エラーメッセージを表示して全体を中断 |
| 音声生成タイムアウト | 15分経過で警告を出してスキップ |
| レート制限（429） | `Retry-After` ヘッダに従って待機 |
| 中断時の再開 | 生成済み MP3 が存在するエピソードはスキップ |

### 2.7 ログ出力

```
[1/117] #01 2進数と小数変換 ― コンピュータの数の扱い方
  関連過去問: 5件
  ソーステキスト: 3,200文字
  ノートブック作成... OK
  ソース追加... OK
  音声生成開始... ポーリング中 (30秒/15分)
  音声生成完了 (2分15秒)
  ダウンロード → podcasts/ep001_2進数と小数変換.mp3 (8.2MB)

[2/117] #02 計算誤差の正体 ― 桁落ち・丸め誤差・情報落ち
  ...

===== 完了 =====
成功: 115/117
スキップ（既存）: 0
失敗: 2 (#45, #89)
```

---

## Step 3: Makefile 更新

既存の `Makefile` に以下のターゲットを追加:

```makefile
.PHONY: podcast podcast-episode podcast-dry-run

podcast:
	python3 generate_podcasts.py --all

podcast-episode:
	python3 generate_podcasts.py --episode $(EP)

podcast-dry-run:
	python3 generate_podcasts.py --all --dry-run
```

使用例:
```bash
make podcast-dry-run         # 全エピソードのコンテンツ確認
make podcast-episode EP=1    # エピソード1だけ生成
make podcast                 # 全エピソード生成
```

---

## Step 4: `.gitignore` 更新

以下を追加:
```
podcasts/
```

---

## 修正対象ファイル一覧

| ファイル | 操作 | 内容 |
|---|---|---|
| `SETUP_GCP.md` | **新規作成** | GCP API セットアップ手順書 |
| `generate_podcasts.py` | **新規作成** | メインスクリプト（約300〜400行想定） |
| `Makefile` | **編集** | podcast ターゲット3つ追加 |
| `.gitignore` | **編集** | `podcasts/` 追加 |

## 参照する既存ファイル（読み取りのみ）

| ファイル | 用途 |
|---|---|
| `episode_list.md` | 117エピソードの定義（タイトル・トピック一覧） |
| `category_taxonomy.md` | カテゴリ階層構造（トピック→分野マッピング） |
| `ap_questions_1000.json` | 過去問データベース（1000問） |

---

## 検証手順

1. **dry-run でコンテンツ確認**
   ```bash
   python3 generate_podcasts.py --episode 1 --dry-run
   ```
   → ソーステキストが正しく構築されること、関連過去問が適切に抽出されることを確認

2. **GCP API 疎通確認**
   ```bash
   gcloud auth print-access-token
   ```

3. **1エピソード生成テスト**
   ```bash
   python3 generate_podcasts.py --episode 1 --project YOUR_PROJECT_ID
   ```
   → `podcasts/ep001_2進数と小数変換.mp3` が生成されること

4. **MP3 再生して品質確認**
   - 内容が正確か
   - 日本語が自然か
   - 過去問の解説が含まれているか

5. **範囲指定テスト**
   ```bash
   python3 generate_podcasts.py --range 1-5
   ```

6. **再開動作の確認**
   - 途中で中断後、同じコマンドを再実行 → 生成済みエピソードがスキップされること

7. **全エピソード生成**
   ```bash
   python3 generate_podcasts.py --all
   ```
