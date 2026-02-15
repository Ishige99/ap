#!/usr/bin/env python3
"""応用情報技術者試験 過去問PDF → 統合Markdown変換スクリプト
ハイブリッド方式:
  - 問題冊子(画像ベースPDF): ページ画像抽出 + Tesseract OCR
  - 解答/講評(テキストベースPDF): PyMuPDF直接テキスト抽出
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import pymupdf

PDF_DIR = Path(__file__).parent.parent / "past_exams" / "pdf"
OUT_DIR = Path(__file__).parent.parent / "past_exams" / "markdown"

SECTIONS = [
    ("am_qs", "午前問題"),
    ("am_ans", "午前解答"),
    ("pm_qs", "午後問題"),
    ("pm_ans", "午後解答"),
    ("pm_cmnt", "午後採点講評"),
]


def make_title(year_id: str) -> str:
    m = re.match(r"(\d{4})(r|h)(\d{2})(h|a|o|tokubetsu)", year_id)
    if not m:
        return year_id
    year, era_code, era_year, season = m.groups()
    era = "令和" if era_code == "r" else "平成"
    season_map = {"h": "春期", "a": "秋期", "o": "10月", "tokubetsu": "特別"}
    season_ja = season_map.get(season, season)
    return f"{era}{int(era_year)}年度{season_ja}"


def group_pdfs(pdf_dir: Path) -> dict:
    groups = defaultdict(dict)
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        name = pdf_path.stem
        if "_ap_" not in name:
            continue
        m = re.match(r"(.+)_ap_(.+)", name)
        if m:
            year_id = m.group(1)
            section = m.group(2)
            groups[year_id][section] = pdf_path
    return dict(groups)


def has_text(pdf_path: Path) -> bool:
    """PDFにテキストが含まれるかチェック"""
    doc = pymupdf.open(str(pdf_path))
    total = sum(len(page.get_text().strip()) for page in doc[:3])
    doc.close()
    return total > 50


def convert_text_pdf(pdf_path: Path, images_dir: Path, prefix: str) -> str:
    """テキストベースPDFをMarkdownに変換"""
    doc = pymupdf.open(str(pdf_path))
    md_parts = []
    img_count = 0

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            md_parts.append(text.strip())

        # 埋め込み画像を抽出
        for img_index, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.n > 4:  # CMYK→RGB
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                img_count += 1
                img_name = f"{prefix}_p{page_num+1}_img{img_count}.png"
                pix.save(str(images_dir / img_name))
                md_parts.append(f"\n![{img_name}](images/{img_name})\n")
            except Exception:
                pass

    doc.close()
    return "\n\n".join(md_parts)


def convert_image_pdf(pdf_path: Path, images_dir: Path, prefix: str) -> str:
    """画像ベースPDFをOCR + ページ画像でMarkdownに変換"""
    doc = pymupdf.open(str(pdf_path))
    md_parts = []

    for page_num, page in enumerate(doc):
        # ページ画像を高解像度で保存
        pix = page.get_pixmap(dpi=200)
        img_name = f"{prefix}_page{page_num+1:03d}.png"
        img_path = images_dir / img_name
        pix.save(str(img_path))

        # Tesseract OCRでテキスト抽出
        ocr_text = ""
        try:
            result = subprocess.run(
                ["tesseract", str(img_path), "stdout", "-l", "jpn+eng", "--psm", "3"],
                capture_output=True, timeout=60
            )
            ocr_text = result.stdout.decode("utf-8", errors="replace").strip()
        except Exception:
            pass

        # Markdown: ページ画像 + OCRテキスト
        md_parts.append(f"### ページ {page_num + 1}\n")
        md_parts.append(f"![{img_name}](images/{img_name})\n")
        if ocr_text:
            md_parts.append(f"\n<details><summary>テキスト (OCR)</summary>\n\n{ocr_text}\n\n</details>\n")

    doc.close()
    return "\n".join(md_parts)


def merge_sections(year_id: str, sections_data: list, out_dir: Path) -> Path:
    title = make_title(year_id)
    lines = [f"# {title} 応用情報技術者試験\n\n"]

    for section_key, section_title, md_text in sections_data:
        lines.append(f"---\n\n## {section_title}\n\n")
        lines.append(md_text)
        lines.append("\n\n")

    md_path = out_dir / f"{year_id}_ap.md"
    md_path.write_text("".join(lines), encoding="utf-8")
    return md_path


def main():
    print("=== 応用情報技術者試験 PDF → Markdown 変換 (ハイブリッド方式) ===\n")

    groups = group_pdfs(PDF_DIR)
    print(f"検出した試験回数: {len(groups)} 回\n")

    if not groups:
        print("ERROR: PDFが見つかりません")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Markerが生成した既存のディレクトリをクリーンアップ
    for d in OUT_DIR.iterdir():
        if d.is_dir():
            shutil.rmtree(d)

    total = len(groups)
    start_time = time.time()

    for idx, (year_id, section_files) in enumerate(sorted(groups.items()), 1):
        title = make_title(year_id)
        exam_start = time.time()
        print(f"[{idx}/{total}] {title} ({year_id})")

        exam_out_dir = OUT_DIR / f"{year_id}_ap"
        images_dir = exam_out_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        sections_data = []
        for section_key, section_title in SECTIONS:
            if section_key not in section_files:
                print(f"  SKIP: {section_title}")
                continue

            pdf_path = section_files[section_key]
            is_text = has_text(pdf_path)
            method = "テキスト" if is_text else "OCR+画像"
            print(f"  {section_title} [{method}]", end="", flush=True)

            try:
                prefix = f"{year_id}_{section_key}"
                if is_text:
                    md_text = convert_text_pdf(pdf_path, images_dir, prefix)
                else:
                    md_text = convert_image_pdf(pdf_path, images_dir, prefix)
                print(f" OK")
                sections_data.append((section_key, section_title, md_text))
            except Exception as e:
                print(f" ERROR: {e}")
                sections_data.append((section_key, section_title, f"*変換エラー: {e}*"))

        md_path = merge_sections(year_id, sections_data, exam_out_dir)
        elapsed_exam = time.time() - exam_start
        print(f"  -> {md_path.name} ({elapsed_exam:.0f}秒)\n")

    elapsed = time.time() - start_time
    print(f"=== 完了 ===")
    print(f"処理時間: {elapsed/60:.1f} 分")
    print(f"出力先: {OUT_DIR}")

    md_files = list(OUT_DIR.rglob("*.md"))
    img_files = list(OUT_DIR.rglob("images/*.png"))
    print(f"Markdownファイル: {len(md_files)} 個")
    print(f"画像ファイル: {len(img_files)} 個")


if __name__ == "__main__":
    main()
