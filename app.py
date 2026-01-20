import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

# --- ページ設定 ---
st.set_page_config(page_title="Poisdex 投稿アーカイブ", layout="wide", page_icon="📊")

# X（Twitter）風のダークモード・クリーンデザイン
st.markdown("""
    <style>
    .stApp { background-color: #f7f9f9; }
    .tweet-box {
        background-color: white;
        border: 1px solid #e1e8ed;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        transition: 0.3s;
    }
    .tweet-box:hover { background-color: #f8f8f8; border-color: #ccc; }
    .user-info { font-weight: bold; color: #0f1419; margin-bottom: 5px; }
    .user-id { color: #536471; font-weight: normal; font-size: 0.9em; }
    .tweet-text { font-size: 1.1em; color: #0f1419; line-height: 1.5; white-space: pre-wrap; }
    .tweet-footer { margin-top: 12px; color: #536471; font-size: 0.85em; border-top: 1px solid #eff3f4; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 @poisdex 実績投稿ギャラリー")
st.caption("指定した期間・反応数に基づき、過去の成果を抽出します")

# --- サイドバーの設定 ---
st.sidebar.header("🔍 フィルター設定")
MY_X_ID = "poisdex"

# 日付範囲の選択
col_date1, col_date2 = st.sidebar.columns(2)
start_date = col_date1.date_input("開始日", datetime.now() - timedelta(days=180))
end_date = col_date2.date_input("終了日", datetime.now())

# いいね数のスライダー
min_faves = st.sidebar.slider("最低いいね数", 0, 1000, 50)

# 表示件数
limit = st.sidebar.selectbox("表示件数", [5, 10, 20, 50], index=1)

# --- データ取得 ---
def fetch_my_best_posts():
    # 検索コマンドを組み立て
    query = f"from:{MY_X_ID} min_faves:{min_faves} since:{start_date} until:{end_date}"
    url = f"https://search.yahoo.co.jp/realtime/search?p={query}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Yahoo!の構造から投稿本文を取得
        posts = soup.find_all(["p", "span"], class_=lambda x: x and ("Tweet_body" in x or "Content" in x))
        
        if not posts:
            st.warning("条件に一致する投稿が見つかりませんでした。")
            return

        st.subheader(f"✨ 条件に一致する投稿（上位 {min(len(posts), limit)} 件）")
        
        for post in posts[:limit]:
            text = post.get_text()
            if len(text) > 5:
                # 投稿カードの生成
                st.markdown(f"""
                <div class="tweet-box">
                    <div class="user-info">poisdex <span class="user-id">@poisdex</span></div>
                    <div class="tweet-text">{text}</div>
                    <div class="tweet-footer">📊 この期間の成果投稿</div>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"データの取得中にエラーが発生しました。")

# --- 実行 ---
if st.sidebar.button("この条件で抽出実行"):
    with st.spinner('取得中...'):
        fetch_my_best_posts()
else:
    st.info("サイドバーの「抽出実行」ボタンを押すと表示が始まります。")
