import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# アプリのタイトル
st.set_page_config(page_title="SNSトレンド監視", layout="wide")
st.title("🔥 リアルタイムSNSトレンド監視")

# --- 設定用のサイドバー ---
st.sidebar.header("検索設定")
search_keyword = st.sidebar.text_input("気になるキーワード", "トレンド")
update_interval = st.sidebar.slider("自動更新の間隔 (秒)", 10, 300, 60)

# --- データを取ってくる関数 ---
def get_trends(keyword):
    # Yahoo!リアルタイム検索から情報を読み取る
    url = f"https://search.yahoo.co.jp/realtime/search?p={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"} # サイトにアクセスするための「名刺」のようなもの
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    items = []
    # 投稿のテキスト部分を抜き出す
    posts = soup.select(".Tweet_body__idmUf")
    
    for post in posts[:10]:
        items.append({"最新の投稿内容": post.get_text()})
    return pd.DataFrame(items)

# --- 画面の表示を更新し続けるループ ---
placeholder = st.empty()

while True:
    with placeholder.container():
        st.subheader(f"「{search_keyword}」に関する今の話題")
        df = get_trends(search_keyword)
        
        if not df.empty:
            st.table(df) # 表形式で表示
            st.info(f"最終更新時刻: {time.strftime('%H:%M:%S')}")
        else:
            st.warning("データが見つかりませんでした。別の言葉で試してください。")
            
    time.sleep(update_interval)