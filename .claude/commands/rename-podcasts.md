`podcast/` ディレクトリの音声ファイル（m4a）を `project_docs/episode_prompts.md` のエピソード番号と対応付けてリネームしてください。

## 前提条件

- ffmpeg がインストール済みであること
- openai-whisper が `.venv` にインストール済みであること（なければ `source .venv/bin/activate && pip install openai-whisper` で入れる）

## 手順

### 1. 現状確認
- `ls podcast/` でファイル一覧を取得
- すでに `#XX` 形式のファイル名がついているものはスキップ対象として把握する
- `episode_prompts.md` から全エピソードのタイトル一覧（`### #XX タイトル ― サブタイトル`）を抽出する

### 2. 冒頭30秒を切り出し＆文字起こし
リネームが必要なファイルそれぞれについて:
1. ffmpeg で冒頭30秒を `/tmp/podcast_clips/` に切り出す
2. whisper（baseモデル、日本語）で文字起こしする
3. 文字起こし結果から「第○回」やトピック内容を読み取り、episode_prompts.md のどのエピソードに対応するか特定する

```bash
# 切り出し
mkdir -p /tmp/podcast_clips
ffmpeg -y -i "podcast/ファイル名.m4a" -t 30 -acodec copy "/tmp/podcast_clips/ファイル名.m4a"

# 文字起こし
source .venv/bin/activate
whisper --model base --language ja --output_format txt /tmp/podcast_clips/*.m4a
```

### 3. マッピングを確定
- 文字起こし結果と episode_prompts.md のエピソード番号・タイトルを照合する
- 対応が不明なファイルがあればユーザーに確認する
- episode_prompts.md に対応しないファイル（シラバス概要回など）は `#00a`, `#00b` 等の番外扱いとする

### 4. リネーム実行
リネーム形式: `#XX メインタイトル ― サブタイトル.m4a`

- episode_prompts.md のフルタイトル（サブタイトル含む）を使用する
- ファイル名に使えない `/` は全角 `／` に変換する
- 例: `#01 2進数と小数変換 ― コンピュータの数の扱い方.m4a`
- 例: `#07 待ち行列理論 ― M／M／1モデルで行列を分析する.m4a`

リネーム前に全マッピング一覧を表示して、ユーザーの確認を取ってから実行すること。

### 5. 検証
- `ls podcast/` でファイルが `#XX` 形式で番号順にリストされることを確認
- ファイル数がリネーム前と変わらないことを確認
- `/tmp/podcast_clips/` を削除して後片付けする
