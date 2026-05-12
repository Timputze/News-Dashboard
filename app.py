import streamlit as st
import psycopg2
import pandas as pd
import os

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

import streamlit as st
import psycopg2
import pandas as pd
import os

DATABASE_URL = os.getenv("DATABASE_URL")


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