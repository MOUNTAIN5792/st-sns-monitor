import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# ページ設定
st.set_page_config(page_title="バズ・埋め込みビューワー", layout="wide", page_icon="✨")

# --- デザインを整えるCSS ---
st.markdown("""
    <style>
    .tweet-card {
        background-color: white;
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .tweet-header {
        color: #657786;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    .tweet-content {
        font-size: 1.1em;
        line-height: 1.5;
        color: #14171a;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ リアルタイム・バズ埋め込み表示")

# サイドバー
st.sidebar.header("検索フィルタ")
default_query = "の min_faves:1000"
search_keyword = st.sidebar.text_input("検索コマンド", default_query)
update_interval = st.sidebar.slider("更新間隔 (秒)", 30, 300, 60)

def get_trends(keyword):
    url = f"https://search.yahoo.co.jp/realtime/search?p={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        items = []
        # 本文とメタ情報を取得
        posts = soup.find_all("article") # 投稿全体を囲むタグを探す
        
        for post in posts[:15]:
            body = post.find(["p", "span"], class_=lambda x: x and "Tweet_body" in x)
            if body:
                items.append({
                    "時刻": datetime.now().strftime("%H:%M"),
                    "内容": body.get_text()
                })
        return items
    except:
        return []

# メイン表示
placeholder = st.empty()

while True:
    with placeholder.container():
        posts_data = get_trends(search_keyword)
        st.write(f"最終更新時刻: {datetime.now().strftime('%H:%M:%S')}")
        
        if posts_data:
            for p in posts_data:
                # HTMLでカード風に表示
                st.markdown(f"""
                <div class="tweet-card">
                    <div class="tweet-header">🕒 {p['時刻']} 取得の注目投稿</div>
                    <div class="tweet-content">{p['内容']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("新しい投稿が見つかりませんでした。")
            
    time.sleep(update_interval)
