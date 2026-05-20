try:
    import streamlit as st
except ImportError as e:
    raise ImportError(
        "streamlit is required to run this application. Install it with 'pip install streamlit' and then rerun."
    ) from e

try:
    import psycopg2
except ImportError as e:
    raise ImportError(
        "psycopg2 is required to run this application. Install it with 'pip install psycopg2-binary' and then rerun."
    ) from e

import pandas as pd
import os

st.set_page_config(layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL")

TOPICS = {
    "EUDI Wallet": ["wallet", "eudi"],
    "eIDAS": ["eidas"],
    "Security": ["pki"],
    "Public Sector": ["ozg", "bsi"],
    "Age Verification": ["age verification"]
}

def assign_topic(title):
    title = title.lower()
    for topic, keywords in TOPICS.items():
        if any(k in title for k in keywords):
            return topic
    return "Other"

@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM news_articles ORDER BY published_at DESC", conn)
    conn.close()
    return df

df = load_data()
df["topic"] = df["title"].apply(assign_topic)

last_update = df["load_timestamp"].max()

if pd.notna(last_update):
    last_update = last_update.strftime("%Y-%m-%d %H:%M")

st.title("📰 Digital Identity Radar")
st.caption(f"Last Article Posted: {last_update}")

# FILTER
selected_topics = st.sidebar.multiselect(
    "Topic",
    df["topic"].unique(),
    default=df["topic"].unique()
)

min_score = st.sidebar.slider("Min score", 0, int(df["score"].max()), 1)

filtered_df = df[
    (df["topic"].isin(selected_topics)) &
    (df["score"] >= min_score)
]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Articles", len(filtered_df))
col2.metric("Sources", filtered_df["source"].nunique())
col3.metric("Avg Score", round(filtered_df["score"].mean(), 1))

st.divider()

# TOP ARTICLES
st.subheader("🔥 Top Articles")

top_df = filtered_df.sort_values(by="score", ascending=False).head(5)

for _, row in top_df.iterrows():
    st.markdown(f"**{row['title']}**")
    st.caption(f"{row['topic']} | {row['source']} | Score {row['score']}")
    st.link_button("Open", row["link"])
    st.divider()

# ALL ARTICLES
st.subheader("All Articles")

for _, row in filtered_df.iterrows():
    st.write(row["title"])
    st.caption(f"{row['topic']} | {row['source']} | Score {row['score']}")
    st.link_button("Open", row["link"])
    st.divider()
