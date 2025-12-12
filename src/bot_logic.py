
import datetime
import hashlib

# 365と互いに素な定数候補
A_CANDIDATES = [1, 2, 4, 7, 8, 11, 13, 14, 16, 17, 19]

def get_char_value(c):
    """
    文字の数値を計算する (仕様書の定義に基づく)
    英字(A-Z, a-z) -> 1~26
    数字(0-9) -> 0~9
    その他 -> 5
    """
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A') + 1
    elif 'a' <= c <= 'z':
        # 大文字として扱う
        return ord(c.upper()) - ord('A') + 1
    elif '0' <= c <= '9':
        return int(c)
    else:
        # 記号(_, 等)
        return 5

def calc_name_value(account_id):
    """アカウントIDの数値合計を算出"""
    return sum(get_char_value(c) for c in account_id)

def calc_name_number(name_value):
    """1〜9の名前ナンバーを算出"""
    return ((name_value - 1) % 9) + 1

def calc_day_number(date_obj):
    """日付(YYYYMMDD)から1〜9の日ナンバーを算出"""
    date_str = date_obj.strftime("%Y%m%d")
    total = sum(int(d) for d in date_str)
    # 1桁になるまで足し合わせる (数秘術的アプローチ)
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total

def get_a_b(name_value):
    """線形変換用の係数 a, b を決定"""
    a = A_CANDIDATES[name_value % len(A_CANDIDATES)]
    b = name_value % 365
    return a, b

def calc_pattern_index(account_id, date_obj):
    """
    アカウントと日付から 1〜365 のパターンインデックスを算出
    閏年の扱いは簡易的に timetuple().tm_yday (1-366) を使用し、
    366の場合は1に戻すか、mod 365 で処理する。
    仕様書通り: ((a * (day_of_year - 1) + b) mod 365) + 1
    """
    day_of_year = date_obj.timetuple().tm_yday
    
    # 閏年の366日目の扱いは仕様に明記がないが、mod 365ロジックなら
    # 366日目は (366-1)=365 -> mod 365 = 0 -> +1 = 1 となり、1月1日と同じパターンになる可能性があるが
    # 許容範囲とする。
    if day_of_year > 365:
        day_of_year = 1 # 簡易的なフォールバック

    name_value = calc_name_value(account_id)
    a, b = get_a_b(name_value)
    
    pattern_index = ((a * (day_of_year - 1) + b) % 365) + 1
    return pattern_index

def get_archetype_label(name_number):
    """名前ナンバーに対応するアーキタイプ名"""
    archetypes = {
        1: "チャレンジャー型（攻め／起業家気質）",
        2: "バランサー型（調整役・人間関係）",
        3: "クリエイター型（発想・企画）",
        4: "ビルダー型（堅実・積み上げ）",
        5: "コミュニケーター型（営業・交渉）",
        6: "プランナー型（分析・戦略）",
        7: "スペシャリスト型（職人・専門性）",
        8: "リーダー型（統率・意思決定）",
        9: "サポーター型（支援・裏方支援）"
    }
    return archetypes.get(name_number, "不明")
