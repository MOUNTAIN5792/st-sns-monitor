import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# ページ設定
st.set_page_config(page_title="SNS画像バズ・モニター", layout="wide", page_icon="📸")

# デザイン設定（画像表示用に最適化）
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .tweet-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    .tweet-text { font-size: 1.1em; color: #1c1e21; line-height: 1.6; white-space: pre-wrap; margin-bottom: 15px; }
    .tweet-img { width: 100%; border-radius: 10px; margin-top: 10px; border: 1px solid #eee; }
    .status-bar { padding: 10px; border-radius: 10px; background: #fff; margin-bottom: 20px; border-left: 5px solid #1da1f2; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 リアルタイム・画像付きバズ監視")

# サイドバー
st.sidebar.header("表示設定")
search_keyword = st.sidebar.text_input("検索コマンド", "の min_faves:1000")
update_interval = st.sidebar.slider("自動更新 (秒)", 30, 300, 60)

def get_trends(keyword):
    url = f"https://search.yahoo.co.jp/realtime/search?p={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        items = []
        
        # 投稿のひとかたまり（article等）を取得
        posts = soup.find_all(["article", "div"], class_=lambda x: x and "Tweet_body" in x)
        
        # クラス名で見つからない場合のバックアップ
        if not posts:
            posts = soup.select('li.Tweet')

        for post in posts[:10]:
            # テキスト取得
            text_elem = post.find(["p", "span"], class_=lambda x: x and "Tweet_body" in x)
            text = text_elem.get_text() if text_elem else ""
            
            # 画像URLの取得（imgタグを探す）
            img_tag = post.find("img", src=lambda x: x and ("twimg.com" in x or "yjimage" in x))
            img_url = img_tag["src"] if img_tag else None

            if len(text) > 5:
                items.append({
                    "時刻": datetime.now().strftime("%H:%M"),
                    "内容": text,
                    "画像": img_url
                })
        return items
    except:
        return []

# 表示エリア
placeholder = st.empty()

while True:
    with placeholder.container():
        posts_data = get_trends(search_keyword)
        st.markdown(f'<div class="status-bar">最終更新: {datetime.now().strftime("%H:%M:%S")} | 注目投稿: {len(posts_data)}件</div>', unsafe_allow_html=True)
        
        if posts_data:
            for p in posts_data:
                # HTML組み立て
                img_html = f'<img src="{p["画像"]}" class="tweet-img">' if p["画像"] else ""
                st.markdown(f"""
                <div class="tweet-container">
                    <div style="color: #657786; font-size: 0.8em; margin-bottom: 5px;">🕒 {p['時刻']}</div>
                    <div class="tweet-text">{p['内容']}</div>
                    {img_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("条件に合う投稿を探索中...")
            
    time.sleep(update_interval)
