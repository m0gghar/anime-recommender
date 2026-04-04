import pandas as pd

# ---------------- LOAD DATA ----------------
df = pd.read_csv("animedataset23.csv")

#Normalize column names (VERY IMPORTANT)
df.columns = df.columns.str.strip()

# Clean values
df["Name"] = df["Name"].astype(str).str.strip()
df["Genre"] = df["Genre"].apply(lambda x: [g.strip() for g in x.split(",")])

# ---------------- HISTORY ----------------
history = []

# ---------------- SEARCH FUNCTION ----------------
def search_anime(name):
    name = name.strip().lower()
    return df[df["Name"].str.lower().str.contains(name)]

# ---------------- HISTORY FUNCTIONS ----------------
def add_to_history(name):
    if name not in history:
        history.append(name)

def show_history():
    if not history:
        print("No search history yet.")
    else:
        print("\n📜 Search History:")
        for i, anime in enumerate(history, 1):
            print(f"{i}. {anime}")

# ---------------- RECOMMENDATION ----------------
def recommend_by_genre(name):
    anime = search_anime(name)

    if anime.empty:
        return None
    
    target_genres = anime.iloc[0]["Genre"]   # now this is a LIST

    # Score based on number of matching genres
    def genre_score(genres):
        return len(set(genres) & set(target_genres))

    recommendations = df.copy(deep=False)

    # Apply scoring
    recommendations["score"] = recommendations["Genre"].apply(genre_score)

    # Keep only those with at least 1 common genre
    recommendations = recommendations[recommendations["score"] > 0]

    # Remove same anime
    recommendations = recommendations[
        recommendations["Name"].str.lower() != name.lower()
    ]

    # Sort by score first, then rating
    recommendations = recommendations.sort_values(
        by=["score", "Rating"], ascending=[False, False]
    )

    return recommendations.head(5)

# ---------------- DISPLAY ----------------
def display_anime(result):
    for _, row in result.iterrows():
        print("\n🎬 Name:", row["Name"])
        print("⭐ Rating:", row["Rating"])
        print("🎭 Genre:", ", ".join(row["Genre"]))
        print("📺 Episodes:", row["Episodes"])
        print("🏢 Studio:", row["Studio"])
        print("📅 Year:", row["Year"])
        print("𝐒𝐘𝐍𝐎𝐏𝐒𝐈𝐒 :", row["Synopsis"])

def display_recommendations(recs):
    if recs is None or recs.empty:
        print("No recommendations found.")
        return
    
    print("\n🔥 Recommended Anime:")
    for i, (_, row) in enumerate(recs.iterrows(), 1):
        print(f"{i}. {row['Name']} ⭐{row['Rating']}")

from collections import Counter

def recommend_from_history():
    if len(history) < 2:
        print("\n⚠ Not enough history for recommendations")
        return
    
    # Get genres of searched anime
    genres = []

    for name in history:
        anime = df[df["Name"].str.lower() == name.lower()]
        if not anime.empty:
            genres.extend(anime.iloc[0]["Genre"])

    if not genres:
        print("No genre data found.")
        return

    # Find most common genre
    most_common_genre = Counter(genres).most_common(1)[0][0]

    # Recommend based on that genre
    recs = df[df["Genre"].apply(lambda g: most_common_genre in g)]
    recs = recs.sort_values(by="Rating", ascending=False)

    print(f"\n🔥 Based on your taste (Genre: {most_common_genre}):")
    
    for i, (_, row) in enumerate(recs.head(5).iterrows(), 1):
        print(f"{i}. {row['Name']} ⭐{row['Rating']}")

def recommend_similar_names(name):
    keyword = name.split()[0].lower()

    recs = df[df["Name"].str.lower().str.contains(keyword)]

    recs = recs[recs["Name"].str.lower() != name.lower()]

    print(f"\n🔗 Related Anime (similar names):")

    for i, (_, row) in enumerate(recs.head(5).iterrows(), 1):
        print(f"{i}. {row['Name']} ⭐{row['Rating']}")                

# ---------------- MAIN MENU ----------------
def main():
    while True:
        print("\n====== ANIME RECOMMENDER ======")
        print("1. Search Anime")
        print("2. Show History")
        print("3. Recommend from History")
        print("4. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            user_input = input("Enter anime name: ").strip()

            result = search_anime(user_input)

            if result.empty:
                print("❌ Anime not found")
            else:
                display_anime(result)
                add_to_history(user_input)

                recs = recommend_by_genre(user_input)
                display_recommendations(recs)

                recommend_similar_names(user_input)

        elif choice == "2":
            show_history()

        elif choice == "3":
            recommend_from_history()

        else:
            print("Invalid choice, try again.")

# ---------------- RUN ----------------
main()


