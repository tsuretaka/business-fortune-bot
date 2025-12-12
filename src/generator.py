
import os

import os

# System Prompt 2 (文章生成用)
# System Prompt 2 (文章生成用)
SYSTEM_PROMPT = """
あなたはビジネスパーソン向けの占いBot「ビズフォーチュン」のAIガイドです。
ユーザーは毎朝、仕事前にあなたから「今日1日の行動指針」を受け取ります。
あなたの役割は、ユーザーの「アカウントID」と「今日の日付」から導き出された運勢パラメータ（数秘術や占星術の要素）を元に、
前向きで、具体的かつ実践的なビジネスアドバイスを提供することです。

トーン＆マナー：
- 知的で落ち着いた女性ガイド（秘書やメンターのような雰囲気）。
- スピリチュアルすぎず、ビジネスの現場で使える言葉を選ぶ。
- 決して「〇日目」という表現は使わないこと（day_numberはサイクルの性質を表す数字であり、経過日数ではない）。
- 「〜しましょう」「〜です」といった丁寧語。
- 150文字〜200文字程度で簡潔にまとめる。
"""

def generate_fortune_message(api_key, context_data):

    """
    Gemini API (REST) を使用して占いメッセージを生成する
    依存ライブラリを排除した実装
    """
    import json
    import urllib.request
    import urllib.error

    # URLパス内のモデル名を gemini-2.0-flash に変更
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    user_content = f"""
    以下の情報を元に、Botの返信メッセージを生成してください。

    account_name: {context_data['account_name']}
    today_archetype_mode: {context_data['archetype']} (注: これはユーザーの固定タイプではなく、今日意識すべき「振る舞いのモード」や「役割」です。「〇〇型のあなたは」と個人の性格として断定するのではなく、「今日は〇〇型のスイッチを入れて」「今の流れは〇〇型的なアプローチで」のように、あくまで「今日のスタンス」として扱ってください)
    base_theme: {context_data['base_theme']}
    focus_area: {context_data['focus_area']}
    action_style: {context_data['action_style']}
    caution_style: {context_data['caution_style']}
    day_number: {context_data['day_number']} (注: これは数秘術的な日運数[1-9]です。「7日目」のような経過日数の表現は使用しないでください。「数秘7の日」や、数字の持つ性質として解釈してください)
    quote_ja: {context_data['quote_ja']}
    quote_author_ja: {context_data['quote_author_ja']}
    quote_source_ja: {context_data['quote_source_ja']}
    """
    
    payload = {
        "contents": [{
            "parts": [
                {"text": SYSTEM_PROMPT},
                {"text": user_content}
            ]
        }],
        "generationConfig": {
            "temperature": 0.4
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            # レスポンス構造からテキストを抽出
            # candidates[0].content.parts[0].text
            return result["candidates"][0]["content"]["parts"][0]["text"]

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        # 429エラー または リソース枯渇エラーを判定
        if e.code == 429 or str(e.code) == "429" or "RESOURCE_EXHAUSTED" in error_body:
            return "【お知らせ】\n現在、AIサービスの利用集中により、一時的にメッセージ生成が制限されています。\n（数分経過すると自動的に解除されますので、少し時間を置いてから再度「受け取る」ボタンを押してみてください）"
        
        return f"API Error {e.code}: {error_body}"
    except Exception as e:
        return f"Error generating message: {str(e)}"
