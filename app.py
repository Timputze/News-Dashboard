import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import psycopg2
import pandas as pd
import os
import plotly.express as px

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

# =========================
# LOAD DATA
# =========================

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

last_update = df["load_timestamp"].max().strftime("%Y-%m-%d %H:%M")

# =========================
# HEADER
# =========================

st.title("📰 Digital Identity News Scanner")

colA, colB = st.columns([3, 1])
colA.caption("Curated insights on eIDAS, EUDI Wallet & Digital Identity")
colB.success("● Live")

st.caption(f"Last ingestion run: {last_update}")
st.markdown(" ")

# =========================
# SIDEBAR
# =========================

st.sidebar.header("🔎 Filters")

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

search_term = st.sidebar.text_input("Search")

st.sidebar.markdown("---")
st.sidebar.caption("Auto-refreshes every morning")

# =========================
# FILTERING
# =========================

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
# KPIs 
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Articles", len(filtered))

with col2:
    st.metric("Topics", filtered["topic"].nunique())

with col3:
    avg_score = round(filtered["score"].mean(), 1) if len(filtered) > 0 else 0
    st.metric("Avg Score", avg_score)

st.caption("Score = number of keyword matches per article")
st.divider()

# =========================
# CHART
# =========================

st.markdown("## 🧩 Topic Distribution")

topic_counts = filtered["topic"].value_counts().reset_index()
topic_counts.columns = ["topic", "count"]

fig = px.pie(topic_counts, names="topic", values="count")

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# CARD FUNCTION
# =========================

def get_score_color(score):
    if score >= 5:
        return "#12B76A"
    elif score >= 3:
        return "#F79009"
    else:
        return "#F04438"


def render_card(title, topic, source, score, link, keywords, unique_id):

    score_color = get_score_color(score)

    keywords_list = str(keywords).split(",")[:5]
    tags = " ".join([
        f"<span style='background:#1A1D24; padding:3px 8px; border-radius:8px; font-size:10px;'>{k.strip()}</span>"
        for k in keywords_list
    ])

    with stylable_container(
        key=f"card_{unique_id}",
        css_styles="""
        {
            background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            border-radius: 16px;
            padding: 18px;
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 12px;
        }
        """
    ):
        st.markdown(f"**{title}**")

        st.markdown(
            f"{topic} • {source} • <span style='color:{score_color}; font-weight:600;'>Score {score}</span>",
            unsafe_allow_html=True
        )

        st.markdown(tags, unsafe_allow_html=True)

        st.link_button("🔗 Open Article", link)

# =========================
# FEATURED ARTICLE
# =========================

if len(filtered) > 0:
    top1 = filtered.sort_values(by="score", ascending=False).iloc[0]

    st.markdown("## ⭐ Featured")

    with stylable_container(
        key="featured",
        css_styles="""
        {
            background: linear-gradient(135deg, rgba(79,139,249,0.25), rgba(0,0,0,0.2));
            border-radius: 18px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        """
    ):
        st.markdown(f"### {top1['title']}")
        st.caption(f"{top1['topic']} • {top1['source']} • Score {top1['score']}")
        st.caption(top1["keywords"])
        st.link_button("🔗 Read Article", top1["link"])

    st.divider()

# =========================
# TOP ARTICLES
# =========================

st.markdown("## 🔥 Top Articles")
st.caption("Highest relevance based on keyword density")

top_df = filtered.sort_values(by="score", ascending=False).head(5)

for i, (_, row) in enumerate(top_df.iterrows()):
    render_card(
        row["title"],
        row["topic"],
        row["source"],
        row["score"],
        row["link"],
        row["keywords"],
        i
    )

st.divider()

# =========================
# ALL ARTICLES
# =========================

st.markdown("## 🗂️ All Articles")

cols = st.columns(2)

for i, (_, row) in enumerate(filtered.iterrows()):
    with cols[i % 2]:
        render_card(
            row["title"],
            row["topic"],
            row["source"],
            row["score"],
            row["link"],
            row["keywords"],
            row["link"]
        )