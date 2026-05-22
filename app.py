import streamlit as st
import psycopg2
import pandas as pd
import os

st.set_page_config(layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# CLIENT TOPICS
# =========================

TOPICS = {
    "LBBW": ["bank", "strategy", "operating"],
    "BA": ["labor", "public", "service"],
    "BMW": ["mobility", "production"],
    "Daimler Truck": ["logistics", "fleet"],
    "E.ON": ["energy", "grid"],
    "Aldi": ["retail", "pricing"],
    "Capgemini": ["consulting", "ai"],
    "ZF": ["automotive", "platform"],
}


def assign_topic(title):
    t = title.lower()
    for client, keywords in TOPICS.items():
        if any(k in t for k in keywords):
            return client
    return "Other"


@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(DATABASE_URL)
    df = pd.read_sql(
        "SELECT * FROM news_articles ORDER BY published_at DESC",
        conn
    )
    conn.close()
    return df


df = load_data()
df["topic"] = df["title"].apply(assign_topic)

last_update = df["load_timestamp"].max()
last_update = last_update.strftime("%Y-%m-%d %H:%M")

# =========================
# UI
# =========================

st.title("📰 Enterprise Model and Strategy News Scanner")
st.caption(f"Last ingestion run: {last_update}")

selected_topics = st.sidebar.multiselect(
    "Client",
    df["topic"].unique(),
    default=df["topic"].unique()
)

min_score = st.sidebar.slider(
    "Minimum relevance",
    0,
    int(df["score"].max()),
    1
)

filtered = df[
    (df["topic"].isin(selected_topics)) &
    (df["score"] >= min_score)
]

# =========================
# KPIs
# =========================

col1, col2, col3 = st.columns(3)
col1.metric("Articles", len(filtered))
col2.metric("Clients", filtered["topic"].nunique())
col3.metric("Avg Score", round(filtered["score"].mean(), 1))

st.divider()

# =========================
# TOP ARTICLES
# =========================

st.subheader("🔥 Top Articles")

top_df = filtered.sort_values(by="score", ascending=False).head(5)

for _, row in top_df.iterrows():
    st.markdown(f"**{row['title']}**")
    st.caption(f"{row['topic']} | {row['source']} | Score {row['score']}")
    st.link_button("Open", row["link"])
    st.divider()

# =========================
# ALL ARTICLES
# =========================

st.subheader("All Articles")

for _, row in filtered.iterrows():
    st.write(row["title"])
    st.caption(f"{row['topic']} | {row['source']} | Score {row['score']}")
    st.link_button("Open", row["link"])
    st.divider()
