
import json
import os
import random
import datetime
import argparse
from bot_logic import calc_name_value, calc_name_number, calc_day_number, calc_pattern_index, get_archetype_label
from generator import generate_fortune_message

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
QUOTES_FILE = os.path.join(DATA_DIR, "quotes.json")
PATTERNS_FILE = os.path.join(DATA_DIR, "patterns.json")

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def choose_quote(category, account_id, date_str, quotes_db):
    """
    指定カテゴリの格言を選択する。
    無ければ全体から選択。
    シード固定により同じ入力なら常に同じ格言が選ばれるようにする。
    """
    candidates = [q for q in quotes_db if q.get("category") == category]
    if not candidates:
        candidates = quotes_db
    
    # シード生成: account_id + date + category
    seed_str = f"{account_id}{date_str}{category}"
    # 文字列を数値シードに変換
    seed_val = sum(ord(c) for c in seed_str) 
    
    random.seed(seed_val)
    return random.choice(candidates)

def main():
    parser = argparse.ArgumentParser(description="Business Fortune Bot Generator")
    parser.add_argument("account_id", help="Target X account ID (screen_name)")
    parser.add_argument("--date", help="Target date YYYYMMDD (default: today)", default=None)
    args = parser.parse_args()

    account_id = args.account_id
    if args.date:
        target_date = datetime.datetime.strptime(args.date, "%Y%m%d").date()
    else:
        target_date = datetime.date.today()
    
    date_str = target_date.strftime("%Y%m%d")

    # データ読み込み
    try:
        quotes_db = load_json(QUOTES_FILE)
        patterns_db = load_json(PATTERNS_FILE) # list of 365 patterns
    except FileNotFoundError as e:
        print(f"Error: Data file not found. {e}")
        return

    # 計算ロジック
    name_value = calc_name_value(account_id)
    name_number = calc_name_number(name_value)
    day_number = calc_day_number(target_date)
    pattern_index = calc_pattern_index(account_id, target_date)
    
    # 1-indexedのpattern_indexを0-indexedの配列アクセスに使用
    pattern_data = patterns_db[pattern_index - 1] 
    archetype_label = get_archetype_label(name_number)
    
    # 格言選択
    quote = choose_quote(pattern_data["quote_category"], account_id, date_str, quotes_db)

    # コンテキスト構築
    context_data = {
        "account_name": account_id,
        "archetype": archetype_label,
        "base_theme": pattern_data["base_theme"],
        "focus_area": pattern_data["focus_area"],
        "action_style": pattern_data["action_style"],
        "caution_style": pattern_data["caution_style"],
        "day_number": day_number,
        "quote_ja": quote["quote_ja"],
        "quote_author_ja": quote["author_ja"], # quote.jsonのキーに合わせる
        "quote_source_ja": quote["source_ja"]  # quote.jsonのキーに合わせる
    }

    print("=== Debug Info ===")
    print(f"Account: {account_id}, Date: {date_str}")
    print(f"Values: Name={name_value}, NameNum={name_number}, DayNum={day_number}, PatternIdx={pattern_index}")
    print(f"Archetype: {archetype_label}")
    print(f"Pattern: {pattern_data}")
    print(f"Quote: {quote['quote_ja']}")
    print("==================\n")

    # APIキー確認
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY environment variable is not set.")
        print("Set it using: export GEMINI_API_KEY='your_key_here'")
        print("Generating mockup response without LLM...\n")
        
        # Mock Response
        print(f"【今日の指針 for @{account_id}】\n")
        print(f"今日のテーマ：\n{pattern_data['base_theme']}を意識する日\n")
        print(f"今日の行動のヒント：\n{pattern_data['action_style']}、{pattern_data['focus_area']}に取り組みましょう。\n")
        print(f"今日のひと言：\n「{quote['quote_ja']}」\n― {quote['author_ja']}（{quote['source_ja']}）")
    else:
        print("Generating message with Gemini API...\n")
        message = generate_fortune_message(api_key, context_data)
        print(message)

if __name__ == "__main__":
    main()
