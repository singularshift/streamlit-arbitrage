import streamlit as st

app2 = st.Page("app2.py", title="Arbitrage Finder", icon="💰")
watchfinder_app = st.Page("watchfinder-app.py", title="Watchfinder.com Scraper", icon="⌚")

pg = st.navigation([app2, watchfinder_app])
st.set_page_config(page_title="Luxury Watch", page_icon="⌚")
pg.run()