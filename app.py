import streamlit as st
import psycopg2
import pandas as pd
import os

st.set_page_config(layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# TOPICS
# =========================

TOPICS = {
    "eIDAS / Regulation": [
        "eidas", "regulation", "trust services",
        "verordnung", "eu-verordnung", "digitale identität eu"
    ],

    "EUDI Wallet": [
        "wallet", "eudi", "digital identity wallet",
        "digitale brieftasche", "eudi wallet", "identity wallet"
    ],

    "Age Verification": [
        "age verification", "altersverifikation",
        "altersprüfung", "jugendschutz"
    ],

    "Public Sector": [
        "ozg", "bsi", "bund", "government",
        "verwaltung", "behörde", "ministerium",
        "onlinezugangsgesetz", "registermodernisierung"
    ],

    "Security": [
        "pki", "encryption", "security",
        "sicherheit", "verschlüsselung",
        "cybersecurity", "it-sicherheit"
    ],

    "Adoption & Usage": [
        "adoption", "usage", "activation",
        "nutzung", "einführung", "verbreitung",
        "akzeptanz", "rollout"
    ]
}

def assign_topic(title):
    t = title.lower()
    for topic, keywords in TOPICS.items():
        if any(k in t for k in keywords):
            return topic
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

st.title("📰 Digital Identity News Scanner")
st.caption("Curated insights on eIDAS, EUDI Wallet & Digital Identity")
st.caption(f"Last ingestion run: {last_update}")

selected_topics = st.sidebar.multiselect(
    "Topics",
    df["topic"].unique(),
    default=df["topic"].unique()
)

min_score = st.sidebar.slider(
    "Minimum relevance",
    0,
    int(df["score"].max()),
    1
)

search_term = st.sidebar.text_input("Search (title or keywords)")

filtered = df[
    (df["topic"].isin(selected_topics)) &
    (df["score"] >= min_score)
]

if search_term:
    filtered = filtered[
        filtered["title"].str.contains(search_term, case=False, na=False) |
        filtered["keywords"].str.contains(search_term, case=False, na=False)
    ]

# =========================
# KPI
# =========================

col1, col2, col3 = st.columns(3)
col1.metric("Articles", len(filtered))
col2.metric("Topics", filtered["topic"].nunique())
col3.metric("Average Score", round(filtered["score"].mean(), 1))

st.caption("Score is the amount of keywords found per article.")

st.divider()

# =========================
# TOP ARTICLES
# =========================

st.subheader("🔥 Top 5 Articles")

top_df = filtered.sort_values(by="score", ascending=False).head(5)

for _, row in top_df.iterrows():
    st.markdown(f"**{row['title']}**")
    st.caption(f"{row['topic']} | {row['source']} | Score {row['score']}")
    st.caption(f"Keywords: {row['keywords']}")
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