import streamlit as st
import datetime
import os
import sys
import base64

# srcディレクトリをパスに追加して bot_logic 等を直接importできるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# また、src/main.py が bot_logic を import しているため、そこでのパス解決も助ける
sys.path.append(os.path.dirname(__file__))

from src.bot_logic import calc_name_value, calc_name_number, calc_day_number, calc_pattern_index, get_archetype_label
from src.generator import generate_fortune_message
# main.py の import エラーを防ぐため、app.py 用に 関数を再定義あるいは直接ロジックを書く方が安全だが
# 取り急ぎ main.py の依存関係を解決する。
try:
    from src.main import load_json, choose_quote, QUOTES_FILE, PATTERNS_FILE
except ModuleNotFoundError:
    # bot_logic が見つからないと言われる場合の最終手段
    from bot_logic import calc_name_value, calc_name_number, calc_day_number, calc_pattern_index, get_archetype_label
    from generator import generate_fortune_message
    from main import load_json, choose_quote, QUOTES_FILE, PATTERNS_FILE

# ページ設定
st.set_page_config(
    page_title="Business Fortune Bot",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSS (ダークモード・プレミアム感)
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .main-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #a8c0ff, #3f2b96);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    @media (max-width: 640px) {
        .main-title {
            font-size: 1.8rem;
        }
    }
    .card {
        background-color: #1f2937;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        border: 1px solid #374151;
    }
    .theme-header {
        font-size: 1.2rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
    }
    .theme-content {
        font-size: 1.8rem;
        font-weight: 600;
        color: #f3f4f6;
        margin-bottom: 1.5rem;
    }
    .quote-box {
        border-left: 4px solid #6366f1;
        padding-left: 1rem;
        margin-top: 1.5rem;
        font-style: italic;
        color: #d1d5db;
    }
    .stButton>button {
        width: 100%;
        background-color: #4f46e5;
        color: white;
        border-radius: 0.5rem;
        height: 3rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        border-color: #4338ca;
    }
    /* X Share Button Styling Override */
    a[kind="primary"] {
        background-color: #1DA1F2 !important;
        border-color: #1DA1F2 !important;
        color: white !important;
        font-weight: bold;
    }
    a[kind="primary"]:hover {
        background-color: #0d8bd9 !important;
        border-color: #0d8bd9 !important;
    }
    
    /* st.info Customization */
    .stAlert {
        background-color: #1f2937;
        color: #e0e0e0;
        border: 1px solid #374151;
        border-radius: 1rem;
    }
    .stAlert > div {
        color: #e0e0e0 !important;
        line-height: 1.6;
    }
    /* Input Label Visibility Fix */
    .stTextInput label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1rem;
    }
    .stTextInput div[data-testid="stMarkdownContainer"] p {
         color: #ffffff !important; 
    }
    /* 吹き出しとガイド画像のスタイル (Flexbox版) */
    .guide-container {
        display: flex;
        align-items: flex-start; /* 上揃え、あるいは center で中央揃え */
        gap: 1rem;
        margin-bottom: 2rem;
        background-color: transparent;
    }
    .guide-icon {
        flex-shrink: 0;
        width: 80px;
        height: 80px;
    }
    .guide-icon img {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 3px solid #4f46e5;
        object-fit: cover;
        object-position: top center;
    }
    .speech-bubble {
        position: relative;
        background: #1f2937;
        border-radius: 1rem;
        padding: 1.2rem;
        color: #e0e0e0;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        flex-grow: 1;
    }
    /* 吹き出しのしっぽ */
    .speech-bubble::after {
        content: '';
        position: absolute;
        left: -10px;
        top: 20px;
        border-style: solid;
        border-width: 10px 10px 10px 0;
        border-color: transparent #374151 transparent transparent;
        display: block;
        width: 0;
        z-index: 1;
    }
    .speech-bubble::before {
        content: '';
        position: absolute;
        left: -9px;
        top: 20px;
        border-style: solid;
        border-width: 10px 10px 10px 0;
        border-color: transparent #1f2937 transparent transparent;
        display: block;
        width: 0;
        z-index: 2;
    }
    /* Streamlit標準UIの非表示化 */
    header[data-testid="stHeader"] {
        visibility: hidden;
    }
    .stDeployButton {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    #MainMenu {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown('<div class="main-title">ビズフォーチュン</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af; margin-bottom: 2rem;'>ビジネスパーソンのための日次行動指針</p>", unsafe_allow_html=True)

# ガイドキャラクターと吹き出し (HTML/CSSで構築)
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

img_b64 = get_image_base64("assets/guide.jpg")
# 画像がない場合のフォールバックアイコン
img_html = f'<img src="data:image/jpeg;base64,{img_b64}" alt="Guide">' if img_b64 else '<div style="font-size:3rem;">👩‍💼</div>'

st.markdown(f"""
<div class="guide-container">
    <div class="guide-icon">
        {img_html}
    </div>
    <div class="speech-bubble">
        毎日頑張るビジネスマンの皆さんへ、今日の仕事がうまく行くようなアドバイスをさせていただきます。<br>
        あなた自身の判断の後押しをするお手伝いとなりますように😊
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# クエリパラメータとロジック制御
# --------------------------------------------------------------------------------

# クエリパラメータ取得
query_params = st.query_params if hasattr(st, "query_params") else st.experimental_get_query_params()
def get_param(key):
    val = query_params.get(key, "")
    if isinstance(val, list):
        return val[0] if val else ""
    return val

initial_id = get_param("id")
initial_date_str = get_param("date")

# 日付の決定（パラメータ指定があれば過去/未来の日付で再現、なければ今日/JST）
JST = datetime.timezone(datetime.timedelta(hours=9))
target_date = datetime.datetime.now(JST).date()
is_shared_view = False

if initial_date_str:
    try:
        target_date = datetime.datetime.strptime(initial_date_str, "%Y%m%d").date()
        is_shared_view = True
    except ValueError:
        pass 

if initial_id:
    is_shared_view = True

# 入力フォーム (初期値設定)
account_id = st.text_input("X Account ID", value=initial_id if initial_id else "", placeholder="Ex: elonmusk", help="X (Twitter) のユーザーIDを @ なしで入力してください")

# 実行トリガー
generate_clicked = st.button("今日の指針を受け取る")

# シェアリンク飛来直後の自動実行判定
# ただしユーザーがフォームを空にしたら実行しない
should_run = generate_clicked or (is_shared_view and account_id)

if should_run:
    if account_id:
        with st.spinner('星の巡りとビジネスロジックを計算中...'):
            # ボタンを押して再計算した場合は、日付を「今日(JST)」にリセットする
            if generate_clicked:
                JST = datetime.timezone(datetime.timedelta(hours=9))
                target_date = datetime.datetime.now(JST).date()
            
            date_str = target_date.strftime("%Y%m%d")
            
            try:
                quotes_db = load_json(QUOTES_FILE)
                patterns_db = load_json(PATTERNS_FILE)
            except Exception as e:
                st.error(f"Data loading error: {e}")
                st.stop()

            name_value = calc_name_value(account_id)
            name_number = calc_name_number(name_value)
            day_number = calc_day_number(target_date)
            pattern_index = calc_pattern_index(account_id, target_date)
            pattern_data = patterns_db[pattern_index - 1]
            
            # 日替わりアーキタイプの計算 (ID値 + 日付値)
            daily_number = ((name_number + day_number - 1) % 9) + 1
            archetype_label = get_archetype_label(daily_number)
            
            quote = choose_quote(pattern_data["quote_category"], account_id, date_str, quotes_db)

            context_data = {
                "account_name": account_id,
                "archetype": archetype_label,
                "base_theme": pattern_data["base_theme"],
                "focus_area": pattern_data["focus_area"],
                "action_style": pattern_data["action_style"],
                "caution_style": pattern_data["caution_style"],
                "day_number": day_number,
                "quote_ja": quote["quote_ja"],
                "quote_author_ja": quote.get("author_ja", quote.get("quote_author_ja")),
                "quote_source_ja": quote.get("source_ja", quote.get("quote_source_ja"))
            }

            # AI生成
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                 st.warning("API Key not found. Showing basic info only.")
                 generated_text = "（APIキー未設定のためAIメッセージは生成されませんでした）"
            else:
                 generated_text = generate_fortune_message(api_key, context_data)

            # --- 結果表示UI ---
            
            st.markdown(f"### 📅 {target_date.strftime('%Y.%m.%d')} | {archetype_label}")
            st.markdown(f"**Theme: {pattern_data['base_theme']} & {pattern_data['focus_area']}**")
            
            st.info(generated_text, icon="🔮")
            
            # Xシェアボタン作成
            base_app_url = "https://business-fortune-bot.streamlit.app" 
            result_url = f"{base_app_url}?id={account_id}&date={date_str}"
            
            share_text = f"""
【Web版 ビズフォーチュン】
本日のテーマ: {pattern_data['base_theme']} / {pattern_data['focus_area']}

ビジネスパーソンのための日次行動指針を受け取りました。
あなたも今日の運勢をチェックしてみませんか？
👇
{result_url}

#ビズフォーチュン #BusinessFortune
"""
            import urllib.parse
            encoded_text = urllib.parse.quote(share_text.strip())
            share_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
            
            st.link_button("Share on X", share_url, type="primary", use_container_width=True)
            
            # シェア閲覧時のナビゲーション
            if is_shared_view:
                st.markdown("---")
                st.markdown(f"<div style='text-align:center'>↑ {account_id} さんの {target_date.strftime('%Y-%m-%d')} の診断結果を表示しています</div>", unsafe_allow_html=True)
                st.write("")
                if st.button("自分も占ってみる（トップに戻る）", type="secondary", use_container_width=True):
                    if hasattr(st, "query_params"):
                         st.query_params.clear()
                    else:
                         st.experimental_set_query_params()
                    st.rerun()

    else:
        # ID空でボタン押下
        if generate_clicked:
            st.warning("Please enter your Account ID.")

# フッター注意書き
st.markdown("""
<div style="text-align: center; font-size: 0.75rem; color: #6b7280; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #374151;">
【このBotの回答はエンタメ目的の“行動ヒント”であり、医学・投資・法律等の専門アドバイスではありません。】
</div>
""", unsafe_allow_html=True)
