import streamlit as st
import psycopg2
import pandas as pd
import os

st.set_page_config(layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL")

TOPICS = {
    "EUDI Wallet": ["wallet", "eudi"],
    "eIDAS": ["eidas"],
    "Security": ["pki", "encryption"],
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
    df = pd.read_sql("""
        SELECT * FROM news_articles ORDER BY published_at DESC
    """, conn)
    conn.close()
    return df

df = load_data()
df["topic"] = df["title"].apply(assign_topic)

last_update = df["load_timestamp"].max()

st.title("Digital Identity Radar")
st.caption(f"Last ingestion run: {last_update}")

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

st.write(f"Articles: {len(filtered_df)}")

for _, row in filtered_df.iterrows():
    st.markdown(f"**{row['title']}**")
    st.caption(f"{row['topic']} | {row['source']} | Score {row['score']}")
    st.link_button("Open", row["link"])
    st.divider()
