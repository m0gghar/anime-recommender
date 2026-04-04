
import streamlit as st
import pandas as pd
from collections import Counter


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Anime Recommender", layout="centered")

st.title("🎌 Anime Recommender")
st.write("Search your favorite og anime and get recommendations 🔥")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("animedataset23.csv")
    df.columns = df.columns.str.strip()
    df["Name"] = df["Name"].astype(str).str.strip()
    # df["Genre"] = df["Genre"].apply(
    # lambda x: [g.strip() for g in str(x).split(",")] if pd.notna(x) else []
    # )
    df["Genre"] = df["Genre"].fillna("").astype(str)
    return df

df = load_data()

# ---------------- SESSION STATE (for history) ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- FUNCTIONS ----------------
def search_anime(name):
    name = name.strip().lower()
    return df[df["Name"].str.lower() == name]

def add_to_history(name):
    if name not in st.session_state.history:
        st.session_state.history.append(name)

def recommend_by_genre(name):
    anime = search_anime(name)

    if anime.empty:
        return None
    
    target_genres = anime.iloc[0]["Genre"]

    def genre_score(genres):
        return len(set(genres) & set(target_genres))

    recs = df.copy()
    recs["score"] = recs["Genre"].apply(genre_score)

    recs = recs[recs["score"] > 0]

    recs = recs[recs["Name"].str.lower() != name.lower()]

    recs = recs.sort_values(by=["score", "Rating"], ascending=[False, False])

    return recs.head(5)

def recommend_from_history():
    history = st.session_state.history

    if len(history) < 2:
        return None, None
    
    genres = []
    for name in history:
        anime = df[df["Name"].str.lower() == name.lower()]
        if not anime.empty:
            genres.extend(anime.iloc[0]["Genre"])

    if not genres:
        return None, None

    most_common = Counter(genres).most_common(1)[0][0]

    recs = df[df["Genre"].apply(lambda g: most_common in g)]
    recs = recs.sort_values(by="Rating", ascending=False)

    return most_common, recs.head(5)

def recommend_similar_names(name):
    keyword = name.split()[0].lower()

    recs = df[df["Name"].str.lower().str.contains(keyword)]
    recs = recs[recs["Name"].str.lower() != name.lower()]

    return recs.head(5)




# ---------------- SIDEBAR FILTER ----------------
st.sidebar.title("⚙️ Filters")

# Convert rating to numeric
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

# Extract unique genres (important: split if multiple genres in one cell)
all_genres = set()

for genres in df["Genre"].dropna():
    for g in genres.split(","):
        all_genres.add(g.strip())

all_genres = sorted(list(all_genres))

# Multi-select genre
selected_genres = st.sidebar.multiselect("Select Genres", all_genres)

# ---------------- FILTER LOGIC ----------------
filtered_df = df.copy()

# Apply genre filter
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genre"].apply(
            lambda x: any(g in x for g in selected_genres) if pd.notna(x) else False
        )
    ]

# Apply rating filter (>= 8)
filtered_df = filtered_df[filtered_df["Rating"] >= 8]






# ---------------- SEARCH UI ----------------

# Input box
user_input = st.text_input("🔍 Enter Anime Name")

# Search button
search_clicked = st.button("Search")

# Session state to avoid repeat search
if "last_search" not in st.session_state:
    st.session_state.last_search = ""

# Trigger search:
# - when button is clicked OR
# - when Enter is pressed (input changes)
if user_input and (search_clicked or st.session_state.last_search != user_input):

    st.session_state.last_search = user_input  # store last search

    result = search_anime(user_input)

    if result.empty:
        st.error("❌ Anime not found")
    else:
        st.success("✅ Anime Found!")

        for _, row in result.iterrows():
            st.subheader(row["Name"])

            col1, col2, col3 = st.columns([1, 2, 3])

            with col1:
                st.image(row["image_url"], use_container_width=True)

            with col2:
                st.write(f"⭐ Rating: {row['Rating']}")
                st.write(f"🎭 Genre: {row['Genre']}")
                st.write(f"📺 Episodes: {row['Episodes']}")
                st.write(f"🏢 Studio: {row['Studio']}")
                st.write(f"📅 Year: {row['Year']}")

            with col3:
                st.write(f"𝐒𝐘𝐍𝐎𝐏𝐒𝐈𝐒 :  {row['Synopsis']}")    

        add_to_history(user_input)



        # Genre Recommendations
        st.markdown("### 🔥 Recommended Anime")
        recs = recommend_by_genre(user_input)

        if recs is not None and not recs.empty:
            for _, row in recs.iterrows():
                col1, col2 = st.columns([1, 3])

                with col1:
                   st.image(row["image_url"], width=100)

                with col2:
                   st.write(f"**{row['Name']}**")
                   st.write(f"⭐ {row['Rating']}")
                   st.write(f"🎯 Match Score: {row['score']}")
        else:
            st.write("No recommendations found.")

        # Similar Names
        st.markdown("### 🔗 Similar Anime")
        sim_recs = recommend_similar_names(user_input)

        for _, row in sim_recs.iterrows():
            st.write(f"👉 {row['Name']} ⭐{row['Rating']}")

# ---------------- HISTORY ----------------
st.markdown("## 📜 Search History")

if st.session_state.history:
    for i, anime in enumerate(st.session_state.history, 1):
        st.write(f"{i}. {anime}")
else:
    st.write("No history yet.")

# ---------------- HISTORY BASED RECOMMEND ----------------
st.markdown("## 🎯 Based on Your Taste")

if st.button("Recommend from History"):
    genre, recs = recommend_from_history()

    if recs is None:
        st.warning("⚠ Not enough history")
    else:
        st.write(f"🔥 Your favorite genre seems to be: **{genre}**")

        for _, row in recs.iterrows():
            st.write(f"👉 {row['Name']} ⭐{row['Rating']}")


#CSS
st.markdown("""
    <style>
    .stApp {
        background:  #080808;
        color: white;
    }
    h1, h2, h3 {
        color: #38bdf8;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
img:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(56,189,248,0.7);
}
</style>
""", unsafe_allow_html=True)



#instruction text for user
st.markdown(
    """
    <div style="
        background-color:#1e1e1e;
        padding:12px;
        border-radius:10px;
        text-align:center;
        font-size:16px;
        margin-top:10px;
        margin-bottom:20px;
    ">
        ⬇️ <b>Details will appear at the bottom of the page. Please scroll down.</b>
    </div>
    """,
    unsafe_allow_html=True
)



#filtered anime section
st.markdown("## 🎯 Filtered Anime")

# 🚫 If no genre selected → show nothing (or message)
if not selected_genres:
    st.info("👈 Select one or more genres from the sidebar to see results")
else:
    if filtered_df.empty:
        st.warning("No anime found with selected genres 😢")
    else:
        cols = st.columns(5)

        for i, (_, anime) in enumerate(filtered_df.head(10).iterrows()):
            with cols[i % 5]:
                st.image(anime["image_url"], use_container_width=True)

                if st.button("Details", key=f"filterbtn_{i}"):
                    st.session_state.selected_anime = anime["Name"]

                st.markdown(
                    f"<p style='text-align:center'>{anime['Name']}</p>",
                    unsafe_allow_html=True
                )




# ---------------- MOST POPULAR SECTION ----------------
st.markdown("## 🌟 Most Popular Anime")

# Clean data
df["Name_clean"] = df["Name"].str.lower().str.strip()

# Ensure Popularity is numeric
df["Scoredby"] = pd.to_numeric(df["Scoredby"], errors="coerce")

# Sort (HIGHER = MORE POPULAR ✅)
top = df.sort_values(by="Scoredby", ascending=False).head(12)

# Layout (3 per row)
cols = st.columns(3)

for i, (_, anime) in enumerate(top.iterrows()):

    with cols[i % 3]:
        st.image(anime["image_url"], use_container_width=True)

        # Clickable poster button
        if st.button("Details", key=f"popbtn_{i}"):
            st.session_state.selected_anime = anime["Name"]

        st.markdown(
            f"<p style='text-align:center'>{anime['Name']}</p>",
            unsafe_allow_html=True
        )
# ---------------- GET CLICKED ANIME ----------------
if "selected_anime" in st.session_state:

    selected_name = st.session_state.selected_anime

    st.markdown("## 🎬 Anime Details")

    selected = search_anime(selected_name)

    if not selected.empty:
        row = selected.iloc[0]

        col1, col2, col3 = st.columns([1, 2, 3])

        with col1:
                st.image(row["image_url"], use_container_width=True)

        with col2:
                st.write(f"⭐ Rating: {row['Rating']}")
                st.write(f"🎭 Genre: {row['Genre']}")
                st.write(f"📺 Episodes: {row['Episodes']}")
                st.write(f"🏢 Studio: {row['Studio']}")
                st.write(f"📅 Year: {row['Year']}")

        with col3:
                st.write(f"𝐒𝐘𝐍𝐎𝐏𝐒𝐈𝐒 :  {row['Synopsis']}")








