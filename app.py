import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# ページ設定
st.set_page_config(page_title="超絶バズ監視ボード", layout="wide", page_icon="🚀")

st.title("🚀 リアルタイム超絶バズ（1000いいね以上）監視")
st.caption("SNS上で今まさに1000いいねを超えている注目の投稿を表示します")

# サイドバーの設定
st.sidebar.header("検索フィルタ")
# 全ての投稿にヒットしやすいように「の」という助詞を検索対象にするのがコツです
default_query = "の min_faves:1000"
search_keyword = st.sidebar.text_input("検索コマンド", default_query)
update_interval = st.sidebar.slider("自動更新の間隔 (秒)", 30, 300, 60)

def get_trends(keyword):
    # Yahoo!リアルタイム検索のURL（最新順に並ぶようパラメータ調整）
    url = f"https://search.yahoo.co.jp/realtime/search?p={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        items = []
        
        # 投稿本文を抽出
        posts = soup.find_all(["p", "span"], class_=lambda x: x and ("Tweet_body" in x or "Content" in x))
        
        for post in posts[:20]: # バズ投稿を多めに20件取得
            text = post.get_text()
            if text and len(text) > 10:
                items.append({
                    "取得時刻": datetime.now().strftime("%H:%M"),
                    "バズ投稿内容": text
                })
        return pd.DataFrame(items)
    except:
        return pd.DataFrame()

# メイン表示エリア
placeholder = st.empty()

while True:
