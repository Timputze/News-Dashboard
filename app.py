import streamlit as st
import psycopg2
import pandas as pd
import os

st.set_page_config(layout="wide")

DATABASE_URL = "postgresql://neondb_owner:npg_ORFd0pJDw3tG@ep-delicate-unit-alea8c7k-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    conn = psycopg2.connect(DATABASE_URL)
    query = """
        SELECT title, link, source, score, published_at
        FROM news_articles
        ORDER BY published_at DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

# =========================
# UI
# =========================

st.title("📰 Digital Identity News")
st.caption("Curated insights on eIDAS, EUDI Wallet & Digital Identity")

# Sidebar filters
st.sidebar.header("Filters")

selected_source = st.sidebar.multiselect(
    "Source",
    options=sorted(df["source"].unique()),
    default=df["source"].unique()
)

min_score = st.sidebar.slider(
    "Minimum keyword hits",
    0,
    int(df["score"].max()),
    1
)

search_term = st.sidebar.text_input("Search")

# Filter logic
filtered_df = df[
    (df["source"].isin(selected_source)) &
    (df["score"] >= min_score)
]

if search_term:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(search_term, case=False, na=False)
    ]

# =========================
# KPIs
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("Articles", len(filtered_df))
col2.metric("Sources", filtered_df["source"].nunique())
col3.metric("Avg Score", round(filtered_df["score"].mean(), 1))

st.markdown("---")

# =========================
# TOP ARTICLES
# =========================

st.subheader("🔥 Top Articles")

top_df = filtered_df.sort_values(by="score", ascending=False).head(5)

for _, row in top_df.iterrows():
    st.markdown(f"### {row['link']}")
    st.caption(f"{row['source']} • Score: {row['score']} • {row['published_at'].date()}")
    st.markdown("---")

# =========================
# ALL ARTICLES
# =========================

st.subheader("📄 All Articles")

for _, row in filtered_df.iterrows():
    st.markdown(f"{row['link']}")
    st.caption(f"{row['source']} • Score: {row['score']} • {row['published_at'].date()}")
