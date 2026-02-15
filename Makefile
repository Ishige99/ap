.PHONY: help setup setup-tesseract download convert extract all site serve clean clean-site clean-all

# デフォルトターゲット: ヘルプを表示
help:
	@echo ""
	@echo "=== 応用情報技術者試験 過去問データパイプライン ==="
	@echo ""
	@echo "【環境構築】"
	@echo "  make setup            Python仮想環境の作成とパッケージのインストール"
	@echo "  make setup-tesseract  Tesseract OCR のインストール案内を表示"
	@echo ""
	@echo "【データパイプライン】(上から順に実行)"
	@echo "  make download         過去問PDFをIPAサイトからダウンロード"
	@echo "  make convert          PDFをMarkdown形式に変換 (OCR含む)"
	@echo "  make extract          Markdownから問題を抽出してJSONを生成"
	@echo "  make all              上記3つを順番にすべて実行"
	@echo ""
	@echo "【サイト】"
	@echo "  make site             サイト用データをビルド (JSON + 画像を docs/ にコピー)"
	@echo "  make serve            ローカルプレビューサーバーを起動 (localhost:8000)"
	@echo ""
	@echo "【クリーンアップ】"
	@echo "  make clean            生成したJSONファイルを削除"
	@echo "  make clean-site       サイト用データを削除 (docs/data, docs/images)"
	@echo "  make clean-all        JSON + Markdown変換結果をすべて削除"
	@echo ""

# --- 環境構築 ---

# Python仮想環境を作成し、必要なパッケージをインストール
setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install pymupdf pymupdf4llm
	@echo ""
	@echo "セットアップ完了。以下のコマンドで仮想環境を有効化してください:"
	@echo "  source .venv/bin/activate"

# Tesseract OCR のインストール案内 (PDF→Markdown変換に必要)
setup-tesseract:
	@echo "Tesseract OCR は PDF の画像ベースページの文字認識に使用します。"
	@echo "以下のコマンドでインストールしてください:"
	@echo ""
	@echo "  brew install tesseract tesseract-lang"
	@echo ""
	@echo "インストール確認:"
	@echo "  tesseract --version"

# --- データパイプライン ---

# 過去問PDFをIPAのWebサイトからダウンロード (2009〜2025年度)
download:
	bash scripts/download_ap_exams.sh

# PDFファイルをMarkdown形式に変換 (画像ベースPDFはOCRで処理)
convert:
	python3 scripts/convert_pdfs.py

# Markdownファイルから問題を抽出・分類し、1000問のJSONデータセットを生成
extract: data/ap_questions_1000.json

data/ap_questions_1000.json: scripts/extract_ap_questions.py past_exams/markdown/*_ap/*_ap.md
	python3 scripts/extract_ap_questions.py

# パイプライン全体を順番に実行 (download → convert → extract)
all: download convert extract

# --- サイト ---

# サイト用データをビルド (JSON + 画像を docs/ にコピー)
site: data/ap_questions_1000.json
	python3 scripts/build_site.py

# ローカルプレビューサーバーを起動
serve: site
	python3 -m http.server 8000 --directory docs

# --- クリーンアップ ---

# 生成したJSONファイルを削除
clean:
	rm -f data/ap_questions_1000.json

# サイト用データを削除
clean-site:
	rm -rf docs/data docs/images

# JSON + Markdown変換結果をすべて削除 (PDFは残す)
clean-all: clean
	rm -rf past_exams/markdown/
