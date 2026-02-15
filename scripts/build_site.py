#!/usr/bin/env python3
"""サイト用データビルドスクリプト

data/ap_questions_1000.json を読み込み、image_path を書き換えて
docs/data/ap_questions.json に出力する。
参照されている画像ファイルのみを docs/images/ にコピーする。
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_JSON = ROOT / "data" / "ap_questions_1000.json"
DST_JSON = ROOT / "docs" / "data" / "ap_questions.json"
DST_IMAGES = ROOT / "docs" / "images"


def main():
    with open(SRC_JSON, encoding="utf-8") as f:
        data = json.load(f)

    copied_images = 0
    skipped_images = 0

    for q in data["questions"]:
        src_path = q.get("image_path", "")
        if not src_path:
            continue

        src_file = ROOT / src_path
        # past_exams/markdown/2010h22a_ap/images/xxx.png -> images/2010h22a_ap/xxx.png
        parts = Path(src_path).parts
        # parts例: ('past_exams', 'markdown', '2010h22a_ap', 'images', 'xxx.png')
        if len(parts) >= 5:
            exam_dir = parts[2]  # 2010h22a_ap
            filename = parts[-1]
            new_path = f"images/{exam_dir}/{filename}"
            q["image_path"] = new_path

            dst_file = ROOT / "docs" / new_path
            if src_file.exists():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
                    copied_images += 1
                else:
                    skipped_images += 1
            else:
                q["image_path"] = ""
        else:
            q["image_path"] = ""

    DST_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(DST_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total = len(data["questions"])
    with_images = sum(1 for q in data["questions"] if q.get("image_path"))
    print(f"=== サイトデータビルド完了 ===")
    print(f"問題数: {total}")
    print(f"画像あり: {with_images}")
    print(f"画像コピー: {copied_images} (スキップ: {skipped_images})")
    print(f"出力: {DST_JSON}")


if __name__ == "__main__":
    main()
