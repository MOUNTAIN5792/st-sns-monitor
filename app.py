import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import urllib.parse

st.set_page_config(page_title="エステー公式アーカイブ", layout="centered")

# Xウィジェット表示用
def render_tweet(tweet_url):
    embed_code = f"""
    <div style="display: flex; justify-content: center;">
        <blockquote class="twitter-tweet" data-conversation="none"><a href="{tweet_url}"></a></blockquote>
    </div>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """
    components.html(embed_code, height=500, scrolling=True)

st.title("🐤 @st_product_info 成果抽出")

# --- サイドバー ---
st.sidebar.header("🔍 抽出条件")
MY_X_ID = "st_product_info"
start_date = st.sidebar.date_input("開始日", datetime.now() - timedelta(days=365)) # 1年に延ばしました
end_date = st.sidebar.date_input("終了日", datetime.now())
min_faves = st.sidebar.slider("最低いいね数", 0, 1000, 50) # 最初は50くらいで試しましょう

if st.sidebar.button("実績を抽出する"):
    # 検索クエリ
    query = f"from:{MY_X_ID} min_faves:{min_faves} since:{start_date} until:{end_date}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_query}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    with st.spinner('探索中...'):
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. まずは「埋め込み」用のURLを探す
        links = soup.find_all("a", href=re.compile(r'status/\d+'))
        tweet_urls = list(dict.fromkeys([l['href'].split('?')[0] for l in links if "twitter.com" in l['href'] or "x.com" in l['href']]))

        # 2. URLが見つかれば「埋め込み」、見つからなければ「テキスト」を表示
        if tweet_urls:
            st.success(f"{len(tweet_urls[:10])}件見つかりました")
            for t_url in tweet_urls[:10]:
                render_tweet(t_url)
        else:
            # URLが拾えない場合、テキストだけでも出す
            posts = soup.find_all(["p", "span"], class_=lambda x: x and "Tweet_body" in x)
            if posts:
                st.info("URLが直接取得できなかったため、テキスト形式で表示します。")
                for p in posts[:10]:
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; padding:15px; border-radius:10px; margin-bottom:10px; background:white;">
                        {p.get_text()}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Yahoo!の検索結果に投稿が表示されませんでした。条件をさらに緩めるか、少し時間を置いて試してください。")
