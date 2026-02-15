# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

応用情報技術者試験（AP）の学習Webアプリケーション。過去問PDF（2009〜2025年度）からデータパイプラインで1000問を抽出・分類し、バニラJavaScript SPAでクイズ形式の学習サイトをGitHub Pagesで提供する。

## ビルドコマンド

```bash
make setup              # .venv作成、pymupdf/pymupdf4llmインストール
make setup-tesseract    # Tesseract OCRのインストール案内（brew）
make download           # IPAサイトから過去問PDF 167件をダウンロード
make convert            # PDF→Markdown変換（画像PDFはOCR処理）
make extract            # 問題抽出・分類 → data/ap_questions_1000.json
make all                # download → convert → extract を順番に実行
make site               # サイト用データビルド（JSON + 画像を docs/ にコピー）
make serve              # localhost:8000 でローカルプレビュー
make clean-site         # docs/data と docs/images を削除
```

Pythonスクリプト実行前に仮想環境を有効化すること: `source .venv/bin/activate`

## アーキテクチャ

### データパイプライン

```
IPA PDF → download_ap_exams.sh → past_exams/pdf/
  → convert_pdfs.py → past_exams/markdown/
  → extract_ap_questions.py → data/ap_questions_1000.json
  → build_site.py → docs/data/ap_questions.json + docs/images/
```

### スクリプト (`scripts/`)

- **download_ap_exams.sh** — IPAから全過去問PDFをダウンロード。既存ファイルはスキップ（冪等）。
- **convert_pdfs.py** — ハイブリッドPDF→Markdown変換。テキストベースPDFは直接抽出、画像ベースPDFはTesseract OCRで処理。ページ画像付きMarkdownを出力。
- **extract_ap_questions.py**（中核、約1200行） — Markdownを解析し、4択問題を抽出。キーワードマッチングで分野/カテゴリ/サブカテゴリに分類、重要度(1-5)と品質スコアを付与、解説を生成。1000問を選定しJSON出力。
- **build_site.py** — 画像パスをWeb用に書き換え、参照される画像のみを `docs/images/` にコピー、`docs/data/ap_questions.json` を出力。

### フロントエンド (`docs/`)

バニラJS SPA。ビルドツール・フレームワーク不使用。GitHub Pagesにデプロイ。

- **app.js** — ハッシュベースルーター（#setup, #home, #category, #quiz, #result, #history, #settings）。ユーザー/トークン未設定時は #setup に強制遷移。
- **questions.js** — 問題JSONの読み込み・キャッシュ、フィルタリング、シャッフル、カテゴリ集計。
- **ui.js** — 全画面の描画: クイズ出題、カテゴリ選択（分野別グループ）、結果と解説表示、学習履歴・統計。
- **storage.js** — localStorageによるユーザー情報、設定、解答履歴の永続化。
- **github.js** — GitHub APIとPATを使い、解答履歴をCSV形式でGitHubリポジトリに保存。

### 問題データモデル

各問題: exam_id, question_number, question_text, choices (ア/イ/ウ/エ), correct_answer, field (テクノロジ/マネジメント/ストラテジ), category (21種), subcategory (65種以上), importance (1-5), quality_score, image_path, explanation

## デプロイ

GitHub Actions (`.github/workflows/deploy.yml`) がmainブランチへのpush時に自動デプロイ: `build_site.py` 実行後、`docs/` をGitHub Pagesに公開。

## 規約

- コミットメッセージ: 英語の要約 + 日本語の詳細 + `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
- `docs/data/` と `docs/images/` はgitignore対象（CIで再生成される）
- コンテンツは日本語、コードのコメントは日本語と英語が混在
