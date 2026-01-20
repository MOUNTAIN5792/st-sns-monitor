import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# ページ設定
st.set_page_config(page_title="SNSバズ・モニター", layout="wide", page_icon="✨")

# デザインをSNSのタイムライン風にするCSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .tweet-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .tweet-time { color: #657786; font-size: 0.8em; margin-bottom: 8px; }
    .tweet-text { font-size: 1.1em; color: #1c1e21; line-height: 1.6; white-space: pre-wrap; }
    .status-bar { padding: 10px; border-radius: 10px; background: #fff; margin-bottom: 20px; border-left: 5px solid #1da1f2; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ リアルタイム・バズ・タイムライン")

# サイドバー
st.sidebar.header("表示設定")
search_keyword = st.sidebar.text_input("検索コマンド", "の min_faves:1000")
update_interval = st.sidebar.slider("自動更新 (秒)", 30, 300, 60)

def get_trends(keyword):
    # Yahoo!リアルタイム検索
    url = f"https://search.yahoo.co.jp/realtime/search?p={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        items = []
        # 投稿全体を包む「section」や「article」をターゲットにする
        posts = soup.find_all(["section", "div"], class_=lambda x: x and ("Tweet_body" in x or "Tweet_content" in x or "Comment_body" in x))
        
        if not posts:
            # 別のクラス名でも試行
            posts = soup.select('div[class*="Tweet_body"], p[class*="Tweet_body"]')

        for post in posts[:15]:
            text = post.get_text().strip()
            if len(text) > 10:
                items.append({
                    "時刻": datetime.now().strftime("%H:%M:%S"),
                    "内容": text
                })
        return items
    except Exception as e:
        return []

# 表示エリア
placeholder = st.empty()

while True:
    with placeholder.container():
        posts_data = get_trends(search_keyword)
        
        st.markdown(f'<div class="status-bar">最終更新: {datetime.now().strftime("%H:%M:%S")} | 取得件数: {len(posts_data)}件</div>', unsafe_allow_html=True)
        
        if posts_data:
            for p in posts_data:
                st.markdown(f"""
                <div class="tweet-container">
                    <div class="tweet-time">🕒 {p['時刻']} 取得</div>
                    <div class="tweet-text">{p['内容']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("現在、新しい投稿を取得できません。以下の理由が考えられます。")
            st.write("1. 1000いいね以上の投稿が今この瞬間に発生していない（数字を 100 に下げてみてください）")
            st.write("2. Yahoo!側で一時的なアクセス制限がかかっている（少し待つか、キーワードを変えてください）")
            
    time.sleep(update_interval)
