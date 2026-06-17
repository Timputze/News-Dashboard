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
st.caption("Curated insights on eIDAS, EUDI Wallet & Digital Identity")

colA, colB = st.columns([3, 1])
colA.caption(f"Last ingestion run: {last_update}")
colB.success("● Live")

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
st.sidebar.caption("Auto-refresh every 5 min")

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
# KPI (cleaner style)
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📰 Articles")
    st.markdown(f"## {len(filtered)}")

with col2:
    st.markdown("### 🧩 Topics")
    st.markdown(f"## {filtered['topic'].nunique()}")

with col3:
    st.markdown("### ⭐ Avg Score")
    avg_score = round(filtered["score"].mean(), 1) if len(filtered) > 0 else 0
    st.markdown(f"## {avg_score}")

st.caption("Score = number of keyword matches per article")

st.divider()

# =========================
# GLASS CARD FUNCTION
# =========================

def render_card(title, topic, source, score, link, keywords):
    st.markdown(f"""
    {link}
        <div style="
            padding:18px;
            border-radius:14px;
            background: rgba(255,255,255,0.04);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom:12px;
        ">
            <div style="font-size:16px; font-weight:600;">
                {title}
            </div>

            <div style="font-size:12px; opacity:0.7; margin-top:6px;">
                {topic} • {source} • Score {score}
            </div>

            <div style="font-size:12px; opacity:0.6; margin-top:6px;">
                {keywords}
            </div>

            <div style="margin-top:10px; font-size:12px; opacity:0.8;">
                🔗 Open Article
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)


# =========================
# TOP ARTICLES
# =========================

st.markdown("## 🔥 Top Articles")
st.caption("Highest relevance based on keyword density")

top_df = filtered.sort_values(by="score", ascending=False).head(5)

for _, row in top_df.iterrows():
    render_card(
        row["title"],
        row["topic"],
        row["source"],
        row["score"],
        row["link"],
        row["keywords"]
    )

st.divider()

# =========================
# ALL ARTICLES
# =========================

st.markdown("## 🗂️ All Articles")

for _, row in filtered.iterrows():
    render_card(
        row["title"],
        row["topic"],
        row["source"],
        row["score"],
        row["link"],
        row["keywords"]
    )
