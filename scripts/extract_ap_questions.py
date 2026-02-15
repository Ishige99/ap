#!/usr/bin/env python3
"""応用情報技術者試験 過去問1000問 問題集作成スクリプト

33回分の午前問題(各80問, 計約2640問)から、21サブカテゴリに分類し
重要度を付与した1000問をJSON形式で出力する。
"""

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

MARKDOWN_DIR = Path(__file__).parent.parent / "past_exams" / "markdown"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "ap_questions_1000.json"
TARGET_COUNT = 1000


def make_title(year_id: str) -> str:
    """exam_idから日本語試験名を生成 (convert_pdfs.pyから流用)"""
    m = re.match(r"(\d{4})(r|h)(\d{2})(h|a|o|tokubetsu)", year_id)
    if not m:
        return year_id
    year, era_code, era_year, season = m.groups()
    era = "令和" if era_code == "r" else "平成"
    season_map = {"h": "春期", "a": "秋期", "o": "10月", "tokubetsu": "特別"}
    season_ja = season_map.get(season, season)
    return f"{era}{int(era_year)}年度{season_ja}"


@dataclass
class Question:
    exam_id: str
    exam_name: str
    question_number: int
    question_text: str
    choices: dict
    correct_answer: str
    field: str  # T/M/S
    category: str = ""
    subcategory: str = ""
    importance: int = 0
    quality_score: float = 0.0
    image_path: str = ""
    explanation: str = ""


# ========== 分野境界マップ ==========

# 年度ごとのT/M/S境界(特殊なもののみ)
FIELD_BOUNDARIES = {
    # 2009-2010: T(1-49), M(50-60), S(61-80)
    "2009h21a": (49, 60),
    "2009h21h": (49, 60),
    "2010h22a": (49, 60),
    "2010h22h": (49, 60),
    # 2011h23a: T(1-49), M(50-59), S(60-80)
    "2011h23a": (49, 59),
    "2011h23tokubetsu": (49, 60),
}
DEFAULT_BOUNDARY = (50, 60)  # T(1-50), M(51-60), S(61-80)


def get_field(exam_id: str, qnum: int) -> str:
    t_end, m_end = FIELD_BOUNDARIES.get(exam_id, DEFAULT_BOUNDARY)
    if qnum <= t_end:
        return "T"
    elif qnum <= m_end:
        return "M"
    else:
        return "S"


# ========== カテゴリ定義 ==========

CATEGORIES = {
    "基礎理論": {
        "keywords": [
            "2進", "補数", "論理式", "論理演算", "ブール", "カルノー",
            "確率", "標準偏差", "正規分布", "分散", "期待値", "ベイズ",
            "行列", "グラフ理論", "BNF", "オートマトン", "形式言語",
            "情報量", "エントロピー", "符号化", "ハミング",
            "サンプリング", "標本化", "PCM", "浮動小数点", "誤差",
            "集合", "ド・モルガン", "待ち行列", "M/M/1", "ポアソン",
            "機械学習", "ニューラルネットワーク", "ディープラーニング",
            "回帰", "クラスタリング", "教師あり", "教師なし",
            "逆行列", "固有値", "最尤", "ユークリッド",
            "交差検証", "ROC", "偽陽性",
            "量子", "ビット列", "基数変換",
        ],
        "range": (1, 10),
        "field": "T",
    },
    "アルゴリズムとプログラミング": {
        "keywords": [
            "アルゴリズム", "ソート", "探索", "二分探索", "ハッシュ",
            "スタック", "キュー", "リスト", "ヒープ",
            "再帰", "計算量", "整列", "連結リスト",
            "プログラム言語", "コンパイラ", "インタプリタ", "リンカ",
            "オブジェクト指向", "関数型", "変数", "配列",
            "XML", "正規表現", "マークアップ",
            "逆ポーランド", "後置表記", "ハフマン",
            "2分探索木", "2分木", "深さ優先", "幅優先",
            "擬似言語", "トレース", "流れ図",
        ],
        "range": (3, 12),
        "field": "T",
    },
    "コンピュータ構成要素": {
        "keywords": [
            "CPU", "プロセッサ", "レジスタ", "キャッシュ", "メモリ",
            "バス", "割込み", "パイプライン", "スーパスカラ", "VLIW",
            "CISC", "RISC", "アドレッシング", "クロック",
            "主記憶", "DMA", "磁気ディスク", "SSD", "RAID",
            "GPU", "FPGA", "SoC", "マイクロプロセッサ",
            "フラッシュメモリ", "実効アクセス", "ヒット率",
            "USB", "シリアル", "パラレル",
            "ファイバチャネル", "NAS", "SAN",
        ],
        "range": (8, 15),
        "field": "T",
    },
    "システム構成要素": {
        "keywords": [
            "信頼性", "MTBF", "MTTR", "稼働率", "可用性",
            "フォールトトレラント", "フェールセーフ", "フェールソフト",
            "デュプレックス", "ホットスタンバイ", "コールドスタンバイ",
            "負荷分散", "クラスタ",
            "スループット", "レスポンス", "ターンアラウンド",
            "ベンチマーク", "性能評価", "並列処理",
            "冗長", "直列", "並列",
            "MIPS", "命令実行",
        ],
        "range": (12, 18),
        "field": "T",
    },
    "ソフトウェア": {
        "keywords": [
            "OS", "オペレーティングシステム", "カーネル", "プロセス",
            "スレッド", "スケジューリング", "デッドロック", "排他制御",
            "ページング", "セグメント", "ファイルシステム",
            "ミドルウェア", "デーモン", "タスク",
            "仮想マシン", "コンテナ",
            "ジョブ", "多重度", "ディスパッチ",
            "OSS", "オープンソース", "ライセンス",
            "スラッシング", "ページフォールト", "LRU",
            "セマフォ", "ミューテックス",
            "ラウンドロビン", "優先度",
        ],
        "range": (15, 22),
        "field": "T",
    },
    "ハードウェア": {
        "keywords": [
            "論理回路", "AND", "OR", "NOT", "NAND", "フリップフロップ",
            "A/D変換", "D/A変換", "センサー", "アクチュエータ",
            "組込み", "マイコン", "LED", "PWM", "タイマー",
            "回転", "モーター", "カウンタ",
            "消費電力", "半導体", "集積回路",
            "真理値表", "加算器", "乗算器",
        ],
        "range": (19, 25),
        "field": "T",
    },
    "データベース": {
        "keywords": [
            "データベース", "SQL", "関係", "テーブル", "正規化",
            "主キー", "外部キー", "ER図", "E-R", "インデックス",
            "トランザクション", "ACID", "ロック",
            "ビュー", "副問合せ", "結合", "射影", "選択",
            "NoSQL", "分散データベース", "レプリケーション",
            "B木", "B+木",
            "DBMS", "RDBMS", "スキーマ",
            "SELECT", "INSERT", "UPDATE", "DELETE",
            "GROUP BY", "ORDER BY", "HAVING",
            "関係代数", "関数従属", "候補キー",
        ],
        "range": (25, 32),
        "field": "T",
    },
    "ネットワーク": {
        "keywords": [
            "ネットワーク", "TCP", "IP", "UDP", "HTTP", "HTTPS",
            "DNS", "DHCP", "NAT", "プロキシ",
            "LAN", "WAN", "VLAN", "ルーティング", "スイッチ",
            "OSI", "レイヤ", "プロトコル", "パケット", "フレーム",
            "サブネット", "CIDR", "IPv4", "IPv6",
            "無線LAN", "Wi-Fi", "Bluetooth",
            "SMTP", "POP", "IMAP", "メール",
            "CSMA", "イーサネット", "帯域",
            "VPN", "SDN",
            "MACアドレス", "IPアドレス", "ポート番号",
            "SNMP", "NTP", "ARP",
        ],
        "range": (30, 38),
        "field": "T",
    },
    "セキュリティ": {
        "keywords": [
            "セキュリティ", "暗号", "認証", "署名", "証明書",
            "公開鍵", "秘密鍵", "共通鍵", "RSA", "AES",
            "ハッシュ", "SHA", "MD5", "ディジタル署名",
            "ファイアウォール", "IDS", "IPS", "WAF",
            "脆弱性", "マルウェア", "ウイルス", "ランサムウェア",
            "不正アクセス", "なりすまし", "フィッシング",
            "XSS", "SQLインジェクション", "CSRF",
            "ISMS", "情報セキュリティ",
            "CRL", "CA", "PKI", "TLS", "SSL",
            "バイオメトリクス", "二要素", "多要素",
            "フォレンジック", "アクセス制御",
            "サイバー", "攻撃", "CSIRT",
            "WPA", "耐タンパ", "ワンタイムパスワード",
            "ソーシャルエンジニアリング", "標的型",
            "チャレンジレスポンス", "Kerberos",
            "DoS", "DDoS", "ボットネット",
            "リスクアセスメント", "リスク分析",
        ],
        "range": (36, 50),
        "field": "T",
    },
    "システム開発技術": {
        "keywords": [
            "ウォーターフォール", "アジャイル", "スクラム", "プロトタイピング",
            "要件定義", "設計", "テスト", "レビュー",
            "UML", "クラス図", "ユースケース", "シーケンス図",
            "モジュール", "結合度", "凝集度", "構造化",
            "ブラックボックス", "ホワイトボックス", "境界値",
            "単体テスト", "結合テスト", "システムテスト",
            "DFD", "状態遷移", "フローチャート",
            "カバレッジ", "回帰テスト",
            "エラー埋込み法",
            "ソフトウェア開発", "工程",
        ],
        "range": (44, 50),
        "field": "T",
    },
    "ソフトウェア開発管理技術": {
        "keywords": [
            "構成管理", "変更管理", "バージョン管理",
            "CMMI", "共通フレーム", "SLCP",
            "リポジトリ", "CASE", "リバースエンジニアリング",
            "再利用", "部品化", "マッシュアップ",
            "DevOps", "CI/CD",
            "リファクタリング",
        ],
        "range": (48, 50),
        "field": "T",
    },
    "プロジェクトマネジメント": {
        "keywords": [
            "プロジェクト", "WBS", "ガントチャート", "PERT",
            "クリティカルパス", "アローダイアグラム",
            "スコープ", "スケジュール", "コスト", "リスク",
            "EVM", "ファンクションポイント",
            "見積", "工数", "人月", "COCOMO",
            "ステークホルダ", "タックマン", "クラッシング",
            "ファストトラッキング",
            "プロジェクトマネジメント", "PMBOK",
        ],
        "range": (51, 55),
        "field": "M",
    },
    "サービスマネジメント": {
        "keywords": [
            "ITIL", "SLA", "SLM", "サービスデスク",
            "インシデント", "問題管理", "変更管理", "リリース管理",
            "キャパシティ管理", "可用性管理",
            "サービスカタログ", "サービスレベル",
            "運用管理", "ヘルプデスク", "エスカレーション",
            "データセンター", "ファシリティ",
            "サービスマネジメント",
            "MTBSI", "FTA", "FMEA",
        ],
        "range": (55, 58),
        "field": "M",
    },
    "システム監査": {
        "keywords": [
            "監査", "内部統制", "コンプライアンス",
            "監査証跡", "監査手続", "監査報告書",
            "試査", "精査",
            "可監査性", "フォローアップ",
            "IT統制", "ITガバナンス",
            "システム監査",
        ],
        "range": (58, 60),
        "field": "M",
    },
    "システム戦略": {
        "keywords": [
            "情報戦略", "IT投資", "EA", "エンタープライズ",
            "SOA", "BPR", "BPM", "業務プロセス",
            "情報システム", "システム化計画",
            "ポートフォリオ", "プログラムマネジメント",
            "DX", "デジタルトランスフォーメーション",
            "データ分析", "アソシエーション",
            "全体最適", "業務改善",
            "SoE", "SoR", "2025年の崖",
        ],
        "range": (61, 65),
        "field": "S",
    },
    "システム企画": {
        "keywords": [
            "RFP", "RFI", "調達",
            "提案書", "見積書", "契約",
            "フィージビリティ", "投資効果", "費用対効果",
            "PBP", "NPV", "IRR", "ROI",
            "要件定義", "要求分析",
        ],
        "range": (63, 67),
        "field": "S",
    },
    "経営戦略マネジメント": {
        "keywords": [
            "経営戦略", "SWOT", "PPM", "バランススコアカード",
            "コアコンピタンス", "ブルーオーシャン",
            "M&A", "アライアンス", "アウトソーシング",
            "CRM", "SCM", "ERP", "SFA",
            "アンゾフ", "ポーター", "5フォース",
            "マーケティング", "4P", "4C",
            "ニッチ", "差別化", "コストリーダーシップ",
            "バリューチェーン", "プロダクトポートフォリオ",
            "BSC", "KPI", "CSF",
        ],
        "range": (67, 72),
        "field": "S",
    },
    "技術戦略マネジメント": {
        "keywords": [
            "技術戦略", "MOT", "イノベーション",
            "ロードマップ", "技術ポートフォリオ",
            "パテント", "特許", "知的財産",
            "デファクトスタンダード", "技術経営",
            "キャズム", "ハイプ",
            "死の谷", "ダーウィンの海",
            "魔の川",
        ],
        "range": (70, 73),
        "field": "S",
    },
    "ビジネスインダストリ": {
        "keywords": [
            "RFID", "POS", "EOS", "EDI",
            "CAD", "CAM", "CAE", "CIM", "FMS",
            "セル生産", "かんばん", "ジャストインタイム",
            "MRP", "生産管理", "在庫管理",
            "PLM", "EC", "電子商取引",
            "コンカレントエンジニアリング",
            "LPWA", "エッジコンピューティング",
            "FinTech", "ブロックチェーン",
        ],
        "range": (71, 76),
        "field": "S",
    },
    "企業活動": {
        "keywords": [
            "損益", "貸借対照表", "キャッシュフロー",
            "利益", "売上", "原価", "固定費", "変動費",
            "損益分岐点", "線形計画法",
            "品質管理", "パレート", "管理図",
            "デシジョンツリー",
            "ABC分析", "PDCA", "自己資本",
            "財務", "会計", "減価償却",
            "リーダーシップ", "OJT",
        ],
        "range": (74, 78),
        "field": "S",
    },
    "法務": {
        "keywords": [
            "著作権", "特許権", "意匠", "商標",
            "個人情報", "プライバシー", "不正競争",
            "労働", "派遣", "請負", "下請",
            "コンプライアンス", "ガバナンス",
            "不正アクセス禁止法", "電子署名法",
            "ソフトウェアライセンス", "GPL",
            "パワーハラスメント",
            "製造物責任", "PL法",
            "守秘義務", "秘密保持",
        ],
        "range": (76, 80),
        "field": "S",
    },
}


# ========== 解答キーパーサー ==========

ANSWER_NORMALIZE = {
    "ア": "ア", "ァ": "ア", "7": "ア",
    "イ": "イ", "4": "イ",
    "ウ": "ウ",
    "エ": "エ", "x": "エ", "=": "エ",
}


def normalize_answer(ans: str) -> str:
    ans = ans.strip()
    if ans in ANSWER_NORMALIZE:
        return ANSWER_NORMALIZE[ans]
    if ans in ("ア", "イ", "ウ", "エ"):
        return ans
    # 全角→半角チェック
    for target in ("ア", "イ", "ウ", "エ"):
        if target in ans:
            return target
    return ans


def parse_answer_key(markdown: str, exam_id: str) -> dict:
    """解答キーをパースして {問番号: (正解, 分野)} を返す"""
    # 午前解答セクションを抽出 (OCRテキスト含むdetailsブロックも含める)
    m = re.search(r"## 午前解答\s*\n(.*?)(?=\n## |\Z)", markdown, re.DOTALL)
    if not m:
        return {}

    section = m.group(1)

    # detailsブロック内のOCRテキストも含めてフラットにする
    detail_pattern = re.compile(
        r"<details><summary>テキスト \(OCR\)</summary>\s*(.*?)\s*</details>",
        re.DOTALL,
    )
    detail_blocks = detail_pattern.findall(section)
    if detail_blocks:
        # OCRテキストを連結
        flat_section = "\n".join(detail_blocks)
    else:
        flat_section = section

    answers = {}

    # Format C: 表形式 (1行に複数の 問N 正解 分野 が並ぶ)
    # 例: "問 1      ア     T        問 21      ウ     T"
    tabular_pattern = re.compile(
        r"(?:問|間|fal|fa\]|fl\]|igs)\s*(\d+)\s+([アイウエァx=4])\s+([TMS])",
    )
    tabular_matches = tabular_pattern.findall(flat_section)
    if len(tabular_matches) >= 40:  # 表形式と判定
        field_map = {"T": "T", "M": "M", "S": "S"}
        for qnum_str, ans_raw, field_raw in tabular_matches:
            qnum = int(qnum_str)
            if 1 <= qnum <= 80:
                ans = normalize_answer(ans_raw)
                field = field_map.get(field_raw, "T")
                answers[qnum] = (ans, field)
        if len(answers) >= 40:
            return answers

    # Format B: 分野フィールドあり (全角Ｔ/Ｍ/Ｓ)
    has_field = "Ｔ" in flat_section or "Ｍ" in flat_section or "Ｓ" in flat_section

    if has_field:
        field_map = {"Ｔ": "T", "Ｍ": "M", "Ｓ": "S", "T": "T", "M": "M", "S": "S"}
        lines = [l.strip() for l in flat_section.split("\n") if l.strip()]
        i = 0
        while i < len(lines):
            qm = re.match(r"問\s*(\d+)", lines[i])
            if qm:
                qnum = int(qm.group(1))
                if 1 <= qnum <= 80 and i + 2 < len(lines):
                    ans = normalize_answer(lines[i + 1])
                    f = lines[i + 2].strip()
                    field = field_map.get(f, "T")
                    answers[qnum] = (ans, field)
                    i += 3
                    continue
            i += 1
    else:
        # Format A: 4列形式 (問1/21/41/61 が同じ行グループ)
        lines = [l.strip() for l in flat_section.split("\n") if l.strip()]
        i = 0
        while i < len(lines):
            qm = re.match(r"問\s*(\d+)", lines[i])
            if qm:
                qnum = int(qm.group(1))
                if 1 <= qnum <= 80:
                    for j in range(i + 1, min(i + 3, len(lines))):
                        ans = normalize_answer(lines[j])
                        if ans in ("ア", "イ", "ウ", "エ"):
                            field = get_field(exam_id, qnum)
                            answers[qnum] = (ans, field)
                            break
            i += 1

    return answers


# ========== 問題テキスト抽出 ==========

# OCRで問番号が誤認識されるパターン
Q_PATTERN = re.compile(
    r"^(?:問|間|Bil|fal|fa\]|igs|PRO|BIT|BIL|問題)\s*(\d{1,2})\s",
    re.MULTILINE,
)


def extract_gozen_ocr(markdown: str, exam_id: str) -> tuple:
    """午前問題セクションのOCRテキストと、テキスト位置→画像パスのマッピングを返す

    Returns:
        (連結OCRテキスト, [(テキスト開始位置, テキスト終了位置, 画像パス), ...])
    """
    gozen_start = markdown.find("## 午前問題")
    gozen_end = markdown.find("## 午前解答")
    if gozen_start == -1 or gozen_end == -1:
        return "", []
    section = markdown[gozen_start:gozen_end]

    # ページごとに画像パスとOCRテキストを取得
    # パターン: ### ページ N → ![...](images/xxx.png) → <details>...</details>
    page_pattern = re.compile(
        r"###\s*ページ\s*\d+\s*\n"
        r".*?!\[.*?\]\((images/[^)]+)\).*?"
        r"<details><summary>テキスト \(OCR\)</summary>\s*(.*?)\s*</details>",
        re.DOTALL,
    )

    blocks = []
    page_map = []  # [(text_start, text_end, image_path)]
    current_pos = 0

    for m in page_pattern.finditer(section):
        img_rel = m.group(1)  # e.g. "images/2024r06a_am_qs_page004.png"
        ocr_text = m.group(2)
        img_path = f"past_exams/markdown/{exam_id}_ap/{img_rel}"

        text_start = current_pos
        text_end = current_pos + len(ocr_text)
        page_map.append((text_start, text_end, img_path))

        blocks.append(ocr_text)
        current_pos = text_end + 2  # +2 for "\n\n" separator

    return "\n\n".join(blocks), page_map


def split_questions(ocr_text: str, page_map: list) -> list:
    """OCRテキストを問題ごとに分割して [(推定番号, テキスト, 画像パス)] を返す"""
    markers = list(Q_PATTERN.finditer(ocr_text))
    if not markers:
        return []

    # フィルタ: 1-80の範囲のみ
    valid = []
    for m in markers:
        try:
            qnum = int(m.group(1))
        except ValueError:
            continue
        if 1 <= qnum <= 89:  # OCRで80が89になるケースに対応
            valid.append((qnum, m.start()))

    def find_image(pos: int) -> str:
        """テキスト位置から対応するページ画像パスを見つける"""
        for text_start, text_end, img_path in page_map:
            if text_start <= pos < text_end:
                return img_path
        # フォールバック: 最も近いページ
        if page_map:
            closest = min(page_map, key=lambda p: abs(p[0] - pos))
            return closest[2]
        return ""

    # テキスト抽出
    questions = []
    for i, (qnum, start) in enumerate(valid):
        end = valid[i + 1][1] if i + 1 < len(valid) else len(ocr_text)
        text = ocr_text[start:end].strip()
        img_path = find_image(start)
        questions.append((qnum, text, img_path))

    return questions


def reconcile_questions(raw_questions: list, answer_keys: dict) -> dict:
    """OCRの問題番号を解答キーと照合して補正し {問番号: (テキスト, 画像パス)} を返す"""
    known_nums = set(answer_keys.keys())
    assigned = {}

    # まず、OCR番号が正しいものをそのまま割り当て
    used_raw = set()
    for i, (qnum, text, img_path) in enumerate(raw_questions):
        if qnum in known_nums and qnum not in assigned:
            assigned[qnum] = (text, img_path)
            used_raw.add(i)

    # 未割り当ての問題を順番に割り当て
    unassigned_nums = sorted(known_nums - set(assigned.keys()))
    unassigned_items = [(i, text, img_path) for i, (_, text, img_path) in enumerate(raw_questions) if i not in used_raw]

    # 文書内の出現順でソート済みなので、対応する番号に割り当て
    for j, num in enumerate(unassigned_nums):
        if j < len(unassigned_items):
            _, text, img_path = unassigned_items[j]
            assigned[num] = (text, img_path)

    return assigned


# ========== 選択肢抽出 ==========

def extract_choices(text: str) -> dict:
    """問題テキストから選択肢を抽出"""
    # OCRの「エエ」を「エ」に正規化
    normalized = re.sub(r"エエ\s", "エ ", text)
    # 「4 」がイの代替（OCR誤認識）の場合がある行頭パターン
    # 「=x」「xr」「=」がエの代替の場合がある
    lines = normalized.split("\n")

    choices = {}

    # パターン1: インライン形式 (ア xxx イ xxx ウ xxx エ xxx) を最初に試す
    for line in lines:
        # 短い選択肢が1行に並ぶ
        m = re.search(r"ア\s+(\S+)\s+イ\s+(\S+)\s+ウ\s+(\S+)\s+エ\s+(\S+)", line)
        if m:
            return {
                "ア": m.group(1),
                "イ": m.group(2),
                "ウ": m.group(3),
                "エ": m.group(4),
            }

    # パターン2: もう少しゆるいインライン (ア text イ text ウ text エ text)
    inline = re.search(
        r"ア\s+(.+?)\s+イ\s+(.+?)\s+ウ\s+(.+?)\s+エ\s+(.+?)$",
        normalized,
        re.MULTILINE,
    )
    if inline:
        return {
            "ア": inline.group(1).strip(),
            "イ": inline.group(2).strip(),
            "ウ": inline.group(3).strip(),
            "エ": inline.group(4).strip(),
        }

    # パターン3: 複数行の選択肢 (ア/イ/ウ/エ で始まる行)
    # 選択肢開始パターン: ア, イ, ウ, エ (+ OCR誤認識の 4, =, xr)
    choice_markers = [
        (re.compile(r"^ア[\s　]"), "ア"),
        (re.compile(r"^イ[\s　]"), "イ"),
        (re.compile(r"^ウ[\s　]"), "ウ"),
        (re.compile(r"^エ[\s　]"), "エ"),
    ]

    choice_lines = {"ア": [], "イ": [], "ウ": [], "エ": []}
    current = None

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        matched = False
        for pattern, marker in choice_markers:
            if pattern.match(line_stripped):
                current = marker
                # マーカー文字(1文字)以降を取得
                rest = line_stripped[1:].strip()
                if rest:
                    choice_lines[marker].append(rest)
                matched = True
                break

        if not matched and current:
            # 次の問題の開始は含めない
            if re.match(r"^(?:問|間|Bil|fal|fa\]|igs|PRO|BIT)", line_stripped):
                break
            choice_lines[current].append(line_stripped)

    for marker, content_lines in choice_lines.items():
        if content_lines:
            choices[marker] = " ".join(content_lines).strip()

    if len(choices) >= 2:
        return choices

    return choices


def extract_question_body(text: str, choices: dict) -> str:
    """問題テキストから問題文本体(選択肢を除く)を抽出"""
    # エエをエに正規化
    text = re.sub(r"エエ\s", "エ ", text)
    # 問番号パターンを除去
    body = re.sub(r"^(?:問|間|Bil|fal|fa\]|igs|PRO|BIT|BIL|問題)\s*\d+\s*", "", text)

    # 選択肢部分を除去
    lines = body.split("\n")
    body_lines = []
    found_choice = False
    for line in lines:
        stripped = line.strip()
        if not found_choice:
            # インライン選択肢 (ア xxx イ xxx ウ xxx エ xxx)
            if re.search(r"ア\s+\S+\s+イ\s+\S+\s+ウ\s+\S+\s+エ\s+\S+", stripped):
                found_choice = True
                continue
            # 行頭のア
            if re.match(r"^ア[\s　]", stripped):
                found_choice = True
                continue
            body_lines.append(line)

    result = "\n".join(body_lines).strip()
    if not result:
        result = body.strip()
    return result


# ========== 品質スコア ==========

def assess_quality(question_text: str, choices: dict) -> float:
    score = 1.0
    if len(choices) < 4:
        score -= 0.3
    if len(choices) < 2:
        score -= 0.3
    if len(question_text) < 20:
        score -= 0.3
    if not re.search(r"[はがのをにでと]", question_text):
        score -= 0.2
    # ゴミ文字の割合
    garbage = len(re.findall(r"[A-Z]{5,}", question_text))
    if garbage > 2:
        score -= 0.1 * min(garbage, 5)
    return max(0.0, min(1.0, score))


# ========== カテゴリ分類 ==========

def classify_question(q: Question) -> str:
    """問題を21カテゴリの1つに分類"""
    text = q.question_text + " " + " ".join(q.choices.values())
    best_cat = ""
    best_score = -1

    for cat_name, config in CATEGORIES.items():
        if config["field"] != q.field:
            continue

        score = 0
        for kw in config["keywords"]:
            if kw.lower() in text.lower() or kw in text:
                score += 1

        # 問題番号位置ボーナス
        q_min, q_max = config["range"]
        if q_min <= q.question_number <= q_max:
            score += 0.5

        if score > best_score:
            best_score = score
            best_cat = cat_name

    if best_score <= 0:
        # フォールバック: 問題番号位置で分類
        return fallback_classify(q)

    return best_cat


def fallback_classify(q: Question) -> str:
    """キーワードが一致しない場合、問題番号位置で分類"""
    for cat_name, config in CATEGORIES.items():
        if config["field"] != q.field:
            continue
        q_min, q_max = config["range"]
        if q_min <= q.question_number <= q_max:
            return cat_name

    # 最終フォールバック
    defaults = {"T": "基礎理論", "M": "サービスマネジメント", "S": "経営戦略マネジメント"}
    return defaults.get(q.field, "基礎理論")


# ========== 子カテゴリ分類 ==========

SUBCATEGORIES = {
    "基礎理論": {
        "離散数学": ["論理式", "集合", "ブール", "カルノー", "ド・モルガン", "命題"],
        "確率・統計": ["確率", "分散", "標準偏差", "正規分布", "ベイズ", "期待値"],
        "数値表現・計算": ["2進", "補数", "浮動小数点", "基数変換", "誤差", "ビット列"],
        "情報理論": ["情報量", "エントロピー", "符号化", "ハミング", "CRC", "サンプリング", "標本化", "PCM"],
        "AI・機械学習": ["機械学習", "ニューラル", "ディープラーニング", "回帰", "交差検証", "ROC", "教師あり", "クラスタリング"],
        "待ち行列・応用数学": ["待ち行列", "M/M/1", "ポアソン", "行列", "逆行列"],
    },
    "アルゴリズムとプログラミング": {
        "データ構造": ["スタック", "キュー", "リスト", "木", "ヒープ", "連結リスト", "2分探索木", "2分木"],
        "探索・整列": ["ソート", "探索", "二分探索", "ハッシュ", "整列", "クイックソート", "マージソート"],
        "プログラム言語・処理系": ["コンパイラ", "インタプリタ", "リンカ", "プログラム言語", "オブジェクト指向", "関数型"],
        "計算量・アルゴリズム設計": ["計算量", "再帰", "逆ポーランド", "ハフマン", "擬似言語", "流れ図", "深さ優先", "幅優先"],
    },
    "コンピュータ構成要素": {
        "プロセッサ": ["CPU", "パイプライン", "RISC", "CISC", "クロック", "スーパスカラ", "VLIW", "プロセッサ", "命令"],
        "メモリ": ["キャッシュ", "主記憶", "ヒット率", "実効アクセス", "フラッシュメモリ", "メモリ"],
        "入出力・ストレージ": ["磁気ディスク", "SSD", "RAID", "USB", "NAS", "SAN", "ファイバチャネル"],
    },
    "システム構成要素": {
        "信頼性設計": ["MTBF", "MTTR", "稼働率", "フォールトトレラント", "冗長", "フェールセーフ", "フェールソフト"],
        "性能評価": ["スループット", "レスポンス", "ターンアラウンド", "MIPS", "ベンチマーク", "性能評価"],
        "システム構成": ["デュプレックス", "クラスタ", "ホットスタンバイ", "負荷分散", "コールドスタンバイ", "直列", "並列"],
    },
    "ソフトウェア": {
        "プロセス管理": ["プロセス", "スレッド", "スケジューリング", "デッドロック", "排他制御", "セマフォ", "ディスパッチ"],
        "メモリ管理": ["ページング", "スラッシング", "仮想記憶", "LRU", "ページフォールト", "セグメント"],
        "OS全般": ["OS", "カーネル", "ファイルシステム", "OSS", "ライセンス", "オペレーティング", "ミドルウェア", "ジョブ"],
    },
    "ハードウェア": {
        "論理回路": ["AND", "OR", "NOT", "NAND", "フリップフロップ", "真理値表", "加算器", "論理回路"],
        "入出力デバイス": ["センサー", "A/D変換", "D/A変換", "アクチュエータ", "LED", "PWM", "モーター"],
        "組込みシステム": ["組込み", "マイコン", "IoT", "LPWA", "エッジ"],
    },
    "データベース": {
        "SQL": ["SELECT", "INSERT", "UPDATE", "DELETE", "GROUP BY", "ORDER BY", "HAVING", "副問合せ", "結合", "ビュー", "SQL"],
        "データベース設計": ["正規化", "ER図", "E-R", "主キー", "外部キー", "関数従属", "スキーマ", "候補キー", "関係代数"],
        "トランザクション": ["トランザクション", "ACID", "ロック", "同時実行", "直列化", "DBMS"],
    },
    "ネットワーク": {
        "TCP/IPプロトコル": ["TCP", "IP", "UDP", "HTTP", "HTTPS", "DNS", "DHCP", "SMTP", "POP", "IMAP", "プロトコル"],
        "ネットワーク構成": ["LAN", "WAN", "VLAN", "ルーティング", "サブネット", "VPN", "スイッチ", "ルータ"],
        "通信技術": ["無線LAN", "Wi-Fi", "CSMA", "帯域", "MACアドレス", "ARP", "SNMP", "NTP", "イーサネット"],
    },
    "セキュリティ": {
        "暗号技術": ["暗号", "公開鍵", "秘密鍵", "共通鍵", "RSA", "AES", "ハッシュ", "SHA", "MD5", "ディジタル署名"],
        "認証・アクセス制御": ["認証", "PKI", "証明書", "バイオメトリクス", "ワンタイムパスワード", "チャレンジレスポンス", "Kerberos", "二要素", "多要素", "アクセス制御"],
        "攻撃・脆弱性": ["マルウェア", "ウイルス", "XSS", "SQLインジェクション", "CSRF", "DoS", "DDoS", "フィッシング", "ランサムウェア", "ソーシャルエンジニアリング", "標的型", "ボットネット", "不正アクセス", "なりすまし"],
        "セキュリティ管理": ["ISMS", "リスク", "CSIRT", "フォレンジック", "情報セキュリティ", "リスクアセスメント"],
        "ネットワークセキュリティ": ["ファイアウォール", "IDS", "IPS", "WAF", "TLS", "SSL", "WPA", "耐タンパ"],
    },
    "システム開発技術": {
        "開発手法": ["ウォーターフォール", "アジャイル", "スクラム", "プロトタイピング", "要件定義"],
        "設計・モデリング": ["UML", "クラス図", "ユースケース", "シーケンス図", "DFD", "状態遷移", "モジュール", "結合度", "凝集度"],
        "テスト技法": ["ブラックボックス", "ホワイトボックス", "境界値", "カバレッジ", "回帰テスト", "単体テスト", "結合テスト", "エラー埋込み"],
    },
    "ソフトウェア開発管理技術": {
        "構成管理": ["構成管理", "バージョン管理", "リポジトリ", "変更管理"],
        "開発プロセス": ["CMMI", "共通フレーム", "SLCP", "DevOps", "CI/CD", "リファクタリング"],
    },
    "プロジェクトマネジメント": {
        "計画・スケジュール": ["WBS", "クリティカルパス", "アローダイアグラム", "PERT", "ガントチャート", "スケジュール", "ファストトラッキング", "クラッシング"],
        "コスト・見積": ["EVM", "ファンクションポイント", "見積", "COCOMO", "工数", "人月", "コスト"],
        "リスク・品質": ["リスク", "品質管理", "ステークホルダ", "タックマン", "スコープ"],
    },
    "サービスマネジメント": {
        "ITIL・サービス運用": ["ITIL", "SLA", "サービスデスク", "エスカレーション", "サービスカタログ"],
        "インシデント・問題管理": ["インシデント", "問題管理", "変更管理", "リリース管理"],
        "可用性・キャパシティ": ["可用性管理", "キャパシティ管理", "ファシリティ", "データセンター"],
    },
    "システム監査": {
        "監査手法": ["監査手続", "試査", "精査", "サンプリング", "監査証跡", "監査報告"],
        "内部統制・ガバナンス": ["内部統制", "ITガバナンス", "コンプライアンス", "IT統制", "フォローアップ"],
    },
    "システム戦略": {
        "情報システム戦略": ["EA", "SOA", "情報戦略", "全体最適", "エンタープライズ"],
        "業務改善・DX": ["BPR", "BPM", "DX", "業務プロセス", "デジタルトランスフォーメーション", "業務改善"],
        "データ活用": ["データ分析", "アソシエーション", "ポートフォリオ", "プログラムマネジメント"],
    },
    "システム企画": {
        "調達・RFP": ["RFP", "RFI", "調達", "提案書", "契約"],
        "投資評価": ["ROI", "NPV", "PBP", "IRR", "フィージビリティ", "投資効果", "費用対効果"],
    },
    "経営戦略マネジメント": {
        "経営分析フレームワーク": ["SWOT", "PPM", "ポーター", "バランススコアカード", "5フォース", "バリューチェーン", "コアコンピタンス", "BSC", "KPI", "CSF"],
        "マーケティング": ["マーケティング", "4P", "4C", "ニッチ", "差別化", "コストリーダーシップ", "プロダクトポートフォリオ"],
        "経営管理システム": ["CRM", "SCM", "ERP", "SFA", "M&A", "アライアンス", "アウトソーシング"],
    },
    "技術戦略マネジメント": {
        "イノベーション": ["イノベーション", "キャズム", "死の谷", "ダーウィンの海", "魔の川", "ハイプ"],
        "技術経営": ["MOT", "ロードマップ", "デファクトスタンダード", "技術経営", "技術戦略", "特許", "知的財産"],
    },
    "ビジネスインダストリ": {
        "生産管理": ["MRP", "セル生産", "かんばん", "ジャストインタイム", "生産管理", "在庫管理", "FMS"],
        "eビジネス": ["EC", "電子商取引", "EDI", "FinTech", "ブロックチェーン"],
        "業務システム": ["POS", "RFID", "CAD", "CAM", "CAE", "CIM", "PLM", "EOS"],
    },
    "企業活動": {
        "財務・会計": ["損益", "貸借対照表", "キャッシュフロー", "減価償却", "自己資本", "財務", "会計", "売上", "利益"],
        "経営工学": ["損益分岐点", "線形計画法", "ABC分析", "パレート", "デシジョンツリー", "管理図", "固定費", "変動費"],
        "組織・人材": ["リーダーシップ", "OJT", "PDCA", "品質管理"],
    },
    "法務": {
        "知的財産権": ["著作権", "特許権", "意匠", "商標"],
        "労働・契約": ["労働", "派遣", "請負", "下請", "パワーハラスメント", "守秘義務"],
        "IT関連法規": ["個人情報", "不正アクセス禁止法", "不正競争", "GPL", "ソフトウェアライセンス", "電子署名法", "製造物責任"],
    },
}


def classify_subcategory(q: Question) -> str:
    """カテゴリ内の子カテゴリを分類"""
    subcats = SUBCATEGORIES.get(q.category)
    if not subcats:
        return ""

    text = q.question_text + " " + " ".join(q.choices.values())
    best_sub = ""
    best_score = 0

    for sub_name, keywords in subcats.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        if score > best_score:
            best_score = score
            best_sub = sub_name

    if best_sub:
        return best_sub

    # フォールバック: 最初の子カテゴリ
    return next(iter(subcats))


# ========== 重要度算定 ==========

def calculate_importance(questions: list) -> None:
    """各問題の重要度を1-5で設定(カテゴリの出題頻度ベース)"""
    category_exam_count = defaultdict(set)
    category_total = defaultdict(int)
    all_exams = set()

    for q in questions:
        category_exam_count[q.category].add(q.exam_id)
        category_total[q.category] += 1
        all_exams.add(q.exam_id)

    total_exams = len(all_exams)
    if total_exams == 0:
        return

    # 各カテゴリの頻度スコア: 平均出題数/回 × 出現率
    category_freq = {}
    for cat in category_total:
        avg_per_exam = category_total[cat] / total_exams
        appearance_rate = len(category_exam_count[cat]) / total_exams
        category_freq[cat] = avg_per_exam * appearance_rate

    # 五分位数で1-5にマッピング
    freqs = sorted(category_freq.values())
    n = len(freqs)
    if n == 0:
        return

    thresholds = [freqs[min(int(n * p), n - 1)] for p in [0.2, 0.4, 0.6, 0.8]]

    for q in questions:
        freq = category_freq.get(q.category, 0)
        importance = 5
        for i, t in enumerate(thresholds):
            if freq <= t:
                importance = i + 1
                break
        q.importance = importance


# ========== 1000問選定 ==========

def select_questions(questions: list, target: int = TARGET_COUNT) -> list:
    """品質・カテゴリ比率・重要度に基づいて問題を選定"""
    # 品質フィルタ
    viable = [q for q in questions if q.quality_score >= 0.4]

    if len(viable) <= target:
        return viable

    # カテゴリごとにグループ化
    by_cat = defaultdict(list)
    for q in viable:
        by_cat[q.category].append(q)

    # 比率に基づく枠割り当て
    total = len(viable)
    allocation = {}
    for cat, qs in by_cat.items():
        proportion = len(qs) / total
        allocation[cat] = max(5, round(proportion * target))

    # 合計をtargetに調整
    current = sum(allocation.values())
    while current > target:
        largest = max(allocation, key=lambda c: allocation[c])
        if allocation[largest] > 5:
            allocation[largest] -= 1
            current -= 1
        else:
            break

    while current < target:
        for cat in sorted(allocation, key=lambda c: len(by_cat[c]) - allocation[c], reverse=True):
            if allocation[cat] < len(by_cat[cat]):
                allocation[cat] += 1
                current += 1
                break
        else:
            break
        if current >= target:
            break

    # 各カテゴリから選定
    selected = []
    for cat, count in allocation.items():
        cat_qs = by_cat[cat]
        # 重要度順 → 品質順 → 新しい年度順
        cat_qs.sort(key=lambda q: (q.importance, q.quality_score, q.exam_id), reverse=True)
        selected.extend(cat_qs[:count])

    return selected


# ========== メイン処理 ==========

def process_exam(md_path: Path) -> list:
    """1つの試験Markdownファイルを処理して問題リストを返す"""
    exam_dir = md_path.parent.name  # e.g. "2024r06a_ap"
    exam_id = exam_dir.replace("_ap", "")
    exam_name = make_title(exam_id)

    markdown = md_path.read_text(encoding="utf-8")

    # 解答キーをパース
    answer_keys = parse_answer_key(markdown, exam_id)
    if not answer_keys:
        print(f"  警告: {exam_id} の解答キーをパースできませんでした", file=sys.stderr)
        return []

    # 午前OCRテキスト抽出 + ページ画像マッピング
    ocr_text, page_map = extract_gozen_ocr(markdown, exam_id)
    if not ocr_text:
        print(f"  警告: {exam_id} の午前問題OCRテキストが見つかりません", file=sys.stderr)
        return []

    # 問題分割
    raw_questions = split_questions(ocr_text, page_map)
    if not raw_questions:
        print(f"  警告: {exam_id} で問題を分割できませんでした", file=sys.stderr)
        return []

    # 問題番号の照合
    question_data = reconcile_questions(raw_questions, answer_keys)

    questions = []
    for qnum in sorted(answer_keys.keys()):
        ans, field = answer_keys[qnum]
        data = question_data.get(qnum)
        if not data:
            continue
        text, img_path = data

        choices = extract_choices(text)
        body = extract_question_body(text, choices)
        quality = assess_quality(body, choices)

        q = Question(
            exam_id=exam_id,
            exam_name=exam_name,
            question_number=qnum,
            question_text=body,
            choices=choices,
            correct_answer=ans,
            field=field,
            quality_score=quality,
            image_path=img_path,
        )
        questions.append(q)

    return questions


def main():
    print("=" * 60)
    print("AP試験 過去問1000問 問題集作成")
    print("=" * 60)

    # Step 1: ファイル探索
    md_files = sorted(MARKDOWN_DIR.glob("*_ap/*_ap.md"))
    print(f"\n対象ファイル数: {len(md_files)}")

    # Step 2-5: 各試験の問題を抽出
    all_questions = []
    for md_path in md_files:
        exam_dir = md_path.parent.name.replace("_ap", "")
        print(f"  処理中: {exam_dir} ...", end=" ")
        questions = process_exam(md_path)
        print(f"{len(questions)}問 抽出")
        all_questions.extend(questions)

    print(f"\n合計抽出数: {len(all_questions)}問")

    # Step 6: カテゴリ分類 + 子カテゴリ分類
    print("\nカテゴリ分類中...")
    for q in all_questions:
        q.category = classify_question(q)
        q.subcategory = classify_subcategory(q)

    # Step 7: 重要度算定
    print("重要度算定中...")
    calculate_importance(all_questions)

    # カテゴリ分布表示
    print("\n--- カテゴリ分布 ---")
    cat_counts = defaultdict(int)
    cat_importance = defaultdict(list)
    for q in all_questions:
        cat_counts[q.category] += 1
        cat_importance[q.category].append(q.importance)

    for cat in CATEGORIES:
        cnt = cat_counts.get(cat, 0)
        avg_imp = (
            sum(cat_importance.get(cat, [0])) / max(len(cat_importance.get(cat, [1])), 1)
        )
        print(f"  {cat}: {cnt}問 (重要度平均: {avg_imp:.1f})")

    # Step 8: 1000問選定
    print(f"\n{TARGET_COUNT}問を選定中...")
    selected = select_questions(all_questions, TARGET_COUNT)
    print(f"選定数: {len(selected)}問")

    # Step 9: JSON出力
    # メタデータ集計
    cat_meta = {}
    sel_cats = defaultdict(list)
    for q in selected:
        sel_cats[q.category].append(q)
    for cat, qs in sorted(sel_cats.items()):
        avg_imp = sum(q.importance for q in qs) / len(qs) if qs else 0
        cat_meta[cat] = {
            "count": len(qs),
            "importance_avg": round(avg_imp, 1),
        }

    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_questions": len(selected),
            "source_exams": len(md_files),
            "total_available": len(all_questions),
            "categories": cat_meta,
        },
        "questions": [
            {
                "id": f"{q.exam_id}_q{q.question_number:02d}",
                "exam_id": q.exam_id,
                "exam_name": q.exam_name,
                "question_number": q.question_number,
                "field": q.field,
                "category": q.category,
                "subcategory": q.subcategory,
                "importance": q.importance,
                "question_text": q.question_text,
                "choices": q.choices,
                "correct_answer": q.correct_answer,
                "quality_score": round(q.quality_score, 2),
                "image_path": q.image_path,
            }
            for q in sorted(selected, key=lambda q: (q.category, -q.importance, q.exam_id))
        ],
    }

    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n出力: {OUTPUT_FILE}")
    print(f"ファイルサイズ: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")

    # サマリー
    print("\n--- 最終サマリー ---")
    print(f"総問題数: {len(selected)}")
    print(f"カテゴリ数: {len(cat_meta)}")
    for cat, meta in sorted(cat_meta.items(), key=lambda x: -x[1]["count"]):
        print(f"  {cat}: {meta['count']}問 (重要度: {meta['importance_avg']})")


if __name__ == "__main__":
    main()
