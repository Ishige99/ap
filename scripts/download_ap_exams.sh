#!/bin/bash
# 応用情報技術者試験(AP) 過去問題 一括ダウンロードスクリプト
# ソース: IPA 独立行政法人 情報処理推進機構
# https://www.ipa.go.jp/shiken/mondai-kaiotu/index.html

BASE_URL="https://www.ipa.go.jp"
DEST_DIR="$(cd "$(dirname "$0")/.." && pwd)/past_exams/pdf"

mkdir -p "$DEST_DIR"

download_pdf() {
    local path="$1"
    local filename=$(basename "$path")
    local dest="$DEST_DIR/$filename"

    if [ -f "$dest" ]; then
        echo "SKIP (exists): $filename"
        return
    fi

    echo "Downloading: $filename"
    curl -sS -L -o "$dest" "${BASE_URL}${path}"

    if [ $? -eq 0 ] && [ -s "$dest" ]; then
        echo "  OK: $filename ($(du -h "$dest" | cut -f1))"
    else
        echo "  FAILED: $filename"
        rm -f "$dest"
    fi
}

echo "=== 応用情報技術者試験 過去問ダウンロード開始 ==="
echo ""

# --- 2009 (H21) ---
echo "--- 2009年度 (平成21年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ug65p90000009bhl-att/2009h21h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000009bhl-att/2009h21h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000009bhl-att/2009h21h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000009bhl-att/2009h21h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000009bhl-att/2009h21h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f3yi-att/2009h21a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f3yi-att/2009h21a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f3yi-att/2009h21a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f3yi-att/2009h21a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f3yi-att/2009h21a_ap_pm_cmnt.pdf"

# --- 2010 (H22) ---
echo "--- 2010年度 (平成22年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ug65p90000004n2z-att/2010h22h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004n2z-att/2010h22h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004n2z-att/2010h22h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004n2z-att/2010h22h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004n2z-att/2010h22h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/ug65p90000004d6f-att/2010h22a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004d6f-att/2010h22a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004d6f-att/2010h22a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004d6f-att/2010h22a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000004d6f-att/2010h22a_ap_pm_cmnt.pdf"

# --- 2011 (H23) ---
echo "--- 2011年度 (平成23年度) ---"
# 特別試験 (春期は東日本大震災で中止)
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ya2-att/2011h23tokubetsu_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ya2-att/2011h23tokubetsu_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ya2-att/2011h23tokubetsu_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ya2-att/2011h23tokubetsu_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ya2-att/2011h23tokubetsu_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ojp-att/2011h23a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ojp-att/2011h23a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ojp-att/2011h23a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ojp-att/2011h23a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000003ojp-att/2011h23a_ap_pm_cmnt.pdf"

# --- 2012 (H24) ---
echo "--- 2012年度 (平成24年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ug65p900000038er-att/2012h24h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000038er-att/2012h24h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000038er-att/2012h24h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000038er-att/2012h24h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000038er-att/2012h24h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/ug65p90000002h5m-att/2012h24a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002h5m-att/2012h24a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002h5m-att/2012h24a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002h5m-att/2012h24a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002h5m-att/2012h24a_ap_pm_cmnt.pdf"

# --- 2013 (H25) ---
echo "--- 2013年度 (平成25年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ug65p90000002e6g-att/2013h25h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002e6g-att/2013h25h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002e6g-att/2013h25h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002e6g-att/2013h25h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000002e6g-att/2013h25h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/ug65p900000027za-att/2013h25a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000027za-att/2013h25a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000027za-att/2013h25a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000027za-att/2013h25a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p900000027za-att/2013h25a_ap_pm_cmnt.pdf"

# --- 2014 (H26) ---
echo "--- 2014年度 (平成26年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ug65p90000001dzu-att/2014h26h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000001dzu-att/2014h26h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000001dzu-att/2014h26h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000001dzu-att/2014h26h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000001dzu-att/2014h26h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/ug65p90000000ye5-att/2014h26a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000ye5-att/2014h26a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000ye5-att/2014h26a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000ye5-att/2014h26a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000ye5-att/2014h26a_ap_pm_cmnt.pdf"

# --- 2015 (H27) ---
echo "--- 2015年度 (平成27年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ug65p90000000f52-att/2015h27h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000f52-att/2015h27h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000f52-att/2015h27h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000f52-att/2015h27h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ug65p90000000f52-att/2015h27h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gxj0-att/2015h27a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gxj0-att/2015h27a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gxj0-att/2015h27a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gxj0-att/2015h27a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gxj0-att/2015h27a_ap_pm_cmnt.pdf"

# --- 2016 (H28) ---
echo "--- 2016年度 (平成28年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gn5o-att/2016h28h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gn5o-att/2016h28h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gn5o-att/2016h28h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gn5o-att/2016h28h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000gn5o-att/2016h28h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000g6fw-att/2016h28a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000g6fw-att/2016h28a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000g6fw-att/2016h28a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000g6fw-att/2016h28a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000g6fw-att/2016h28a_ap_pm_cmnt.pdf"

# --- 2017 (H29) ---
echo "--- 2017年度 (平成29年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fzx1-att/2017h29h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fzx1-att/2017h29h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fzx1-att/2017h29h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fzx1-att/2017h29h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fzx1-att/2017h29h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fqpm-att/2017h29a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fqpm-att/2017h29a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fqpm-att/2017h29a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fqpm-att/2017h29a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fqpm-att/2017h29a_ap_pm_cmnt.pdf"

# --- 2018 (H30) ---
echo "--- 2018年度 (平成30年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fabr-att/2018h30h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fabr-att/2018h30h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fabr-att/2018h30h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fabr-att/2018h30h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000fabr-att/2018h30h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f01f-att/2018h30a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f01f-att/2018h30a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f01f-att/2018h30a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f01f-att/2018h30a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000f01f-att/2018h30a_ap_pm_cmnt.pdf"

# --- 2019 (H31/R01) ---
echo "--- 2019年度 (平成31年度/令和元年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000ddiw-att/2019h31h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000ddiw-att/2019h31h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000ddiw-att/2019h31h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000ddiw-att/2019h31h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000ddiw-att/2019h31h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000dict-att/2019r01a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000dict-att/2019r01a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000dict-att/2019r01a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000dict-att/2019r01a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000dict-att/2019r01a_ap_pm_cmnt.pdf"

# --- 2020 (R02) ---
echo "--- 2020年度 (令和2年度) ---"
# 10月試験のみ (春期はCOVID-19で中止)
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d05l-att/2020r02o_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d05l-att/2020r02o_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d05l-att/2020r02o_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d05l-att/2020r02o_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d05l-att/2020r02o_ap_pm_cmnt.pdf"

# --- 2021 (R03) ---
echo "--- 2021年度 (令和3年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d5ru-att/2021r03h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d5ru-att/2021r03h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d5ru-att/2021r03h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d5ru-att/2021r03h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000d5ru-att/2021r03h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000apad-att/2021r03a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000apad-att/2021r03a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000apad-att/2021r03a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000apad-att/2021r03a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt8000000apad-att/2021r03a_ap_pm_cmnt.pdf"

# --- 2022 (R04) ---
echo "--- 2022年度 (令和4年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/gmcbt80000009sgk-att/2022r04h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000009sgk-att/2022r04h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000009sgk-att/2022r04h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000009sgk-att/2022r04h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000009sgk-att/2022r04h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/gmcbt80000008smf-att/2022r04a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000008smf-att/2022r04a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000008smf-att/2022r04a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000008smf-att/2022r04a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/gmcbt80000008smf-att/2022r04a_ap_pm_cmnt.pdf"

# --- 2023 (R05) ---
echo "--- 2023年度 (令和5年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/ps6vr70000010d6y-att/2023r05a_ap_pm_cmnt.pdf"

# --- 2024 (R06) ---
echo "--- 2024年度 (令和6年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06a_ap_pm_cmnt.pdf"

# --- 2025 (R07) ---
echo "--- 2025年度 (令和7年度) ---"
# 春期
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07h_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07h_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07h_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07h_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07h_ap_pm_cmnt.pdf"
# 秋期
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07a_ap_am_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07a_ap_am_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07a_ap_pm_qs.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07a_ap_pm_ans.pdf"
download_pdf "/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07a_ap_pm_cmnt.pdf"

echo ""
echo "=== ダウンロード完了 ==="
echo ""
echo "ファイル数: $(ls -1 "$DEST_DIR"/*.pdf 2>/dev/null | wc -l) 個"
echo "合計サイズ: $(du -sh "$DEST_DIR" | cut -f1)"
