import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# ページ設定
st.set_page_config(page_title="エステー話題監視", layout="wide")

st.title("🔥 エステー リアルタイム話題監視")

# サイドバーの設定
st.sidebar.header("検索設定")
# 初めから「エステー 100いいね以上」で検索するように設定
search_keyword = st.sidebar.text_input("キーワード", "エステー min_faves:100")
update_interval = st.sidebar.slider("自動更新の間隔 (秒)", 30, 300, 60)

def get_trends(keyword):
    # Yahoo!リアルタイム検索のURL
    url = f"https://search.yahoo.co.jp/realtime/search?p={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        items = []
        
        # 投稿本文を抽出（最新の複数のクラス名に対応）
        posts = soup.find_all(["p", "span"], class_=lambda x: x and ("Tweet_body" in x or "Content" in x))
        
        for post in posts[:15]:
            text = post.get_text()
            if text and len(text) > 5: # 短すぎるゴミデータを除外
                items.append({
                    "時刻": datetime.now().strftime("%H:%M"),
                    "投稿内容": text
                })
        return pd.DataFrame(items)
    except:
        return pd.DataFrame()

# メイン表示
placeholder = st.empty()

while True:
    with placeholder.container():
        df = get_trends(search_keyword)
        
        if not df.empty:
            st.write(f"最終更新: {datetime.now().strftime('%H:%M:%S')}")
            st.table(df) # tableを使うと一覧性が高まります
        else:
            st.warning(f"「{search_keyword}」に一致する新しい投稿がまだありません。条件（数字）を緩めるか、しばらくお待ちください。")
            
    time.sleep(update_interval)
