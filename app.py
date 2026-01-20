import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import urllib.parse

# ページ設定
st.set_page_config(page_title="エステー公式投稿アーカイブ", layout="centered", page_icon="🐤")

# X（Twitter）のウィジェット用JavaScriptを読み込む関数
def render_tweet(tweet_url):
    embed_code = f"""
    <div style="display: flex; justify-content: center;">
        <blockquote class="twitter-tweet" data-conversation="none" data-theme="light">
            <a href="{tweet_url}"></a>
        </blockquote>
    </div>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """
    components.html(embed_code, height=600, scrolling=True)

st.title("🐤 @st_product_info 成果投稿抽出")
st.caption("エステー公式アカウントの過去のバズ投稿を公式埋め込みで再現します")

# --- サイドバー：検索条件 ---
st.sidebar.header("🔍 抽出条件")
MY_X_ID = "st_product_info"

# 期間指定（初期値は直近180日）
start_date = st.sidebar.date_input("開始日", datetime.now() - timedelta(days=180))
end_date = st.sidebar.date_input("終了日", datetime.now())

# いいね数フィルター
min_faves = st.sidebar.slider("最低いいね数", 0, 5000, 100)

# 実行ボタン
if st.sidebar.button("実績を抽出する"):
    # Yahoo!リアルタイム検索用のクエリ作成
    # 書式: from:ID min_faves:数字 since:YYYY-MM-DD until:YYYY-MM-DD
    query = f"from:{MY_X_ID} min_faves:{min_faves} since:{start_date} until:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_query}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    with st.spinner('エステーの過去投稿を探索中...'):
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 投稿URL（twitter.com/x.com の status を含むもの）を正規表現で探す
            links = soup.find_all("a", href=re.compile(r'(twitter\.com|x\.com)/.+/status/\d+'))
            
            # URLを重複なくリスト化（クエリパラメータを除去）
            tweet_urls = []
            for l in links:
                base_url = l['href'].split('?')[0]
                if base_url not in tweet_urls:
                    tweet_urls.append(base_url)
            
            if tweet_urls:
                st.success(f"{len(tweet_urls[:10])}件のバズ投稿が見つかりました（上位10件を表示）")
                for t_url in tweet_urls[:10]:
                    render_tweet(t_url)
            else:
                st.warning("条件に一致する投稿が見つかりませんでした。開始日を古くするか、いいね数を下げてみてください。")
                
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
else:
    st.info("サイドバーの「実績を抽出する」ボタンを押すと、エステー公式の過去投稿が表示されます。")
