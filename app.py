import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Poisdex Archive", layout="centered")

st.title("🏆 @poisdex 成果投稿アーカイブ")
st.caption("公式APIを使わず、高度な検索コマンドで過去のバズを抽出します")

# --- サイドバー：期間とフィルター ---
st.sidebar.header("🔍 フィルター設定")
MY_X_ID = "poisdex"
start_date = st.sidebar.date_input("開始日", datetime.now() - timedelta(days=180))
end_date = st.sidebar.date_input("終了日", datetime.now())
min_faves = st.sidebar.slider("最低いいね数", 0, 1000, 50)

# --- Xの「本物」の埋め込みを作成する関数 ---
def render_tweet(tweet_url):
    embed_code = f"""
    <blockquote class="twitter-tweet" data-conversation="none">
        <a href="{tweet_url}"></a>
    </blockquote>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """
    components.html(embed_code, height=600, scrolling=True)

# --- データ取得ロジック ---
def get_posts():
    # 期間指定といいね数を検索コマンド化
    query = f"from:{MY_X_ID} min_faves:{min_faves} since:{start_date} until:{end_date}"
    url = f"https://search.yahoo.co.jp/realtime/search?p={query}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 投稿のリンク（URL）を抽出する
    links = soup.find_all("a", href=re.compile(r'twitter.com/.*/status/|x.com/.*/status/'))
    
    # 重複を除去してURLリストを作成
    urls = list(dict.fromkeys([l['href'].split('?')[0] for l in links]))
    
    if not urls:
        st.warning("条件に一致する投稿URLが見つかりませんでした。条件を緩めてください。")
        return

    st.success(f"{len(urls[:10])}件の投稿が見つかりました")
    
    # 上位10個を本物の埋め込みで表示
    for tweet_url in urls[:10]:
        render_tweet(tweet_url)

if st.sidebar.button("実績を抽出して表示"):
    get_posts()
