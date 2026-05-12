import streamlit as st
import psycopg2
import pandas as pd

# =========================
# CONFIG
# =========================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "digital_identity_news",
    "user": "postgres",
    "password": "password"
}

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
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

st.title("📰 Digital Identity News Dashboard")

# Filters
st.sidebar.header("Filters")

selected_source = st.sidebar.multiselect(
    "Source",
    options=df["source"].unique(),
    default=df["source"].unique()
)

min_score = st.sidebar.slider("Minimum keyword hits", 0, int(df["score"].max()), 1)

# Apply filters
filtered_df = df[
    (df["source"].isin(selected_source)) &
    (df["score"] >= min_score)
]

# =========================
# DISPLAY
# =========================

st.write(f"Showing {len(filtered_df)} articles")

for _, row in filtered_df.iterrows():
    st.markdown(f"**{row['link']}**")
    st.write(f"Source: {row['source']} | Score: {row['score']} | Date: {row['published_at']}")
    st.write("---")
