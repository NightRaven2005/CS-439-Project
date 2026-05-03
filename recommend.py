import sqlite3
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances

def recommend_heroes():
    conn = sqlite3.connect("mlbb_database.db")
    df = pd.read_sql_query("SELECT * FROM clustered_hero_stats", conn)
    conn.close()

    hero_name = input("Enter a hero name: ").lower().strip()

    # Normalize names
    df["hero_name_clean"] = df["hero_name"].str.lower().str.strip()

    selected = df[df["hero_name_clean"] == hero_name]

    if selected.empty:
        print("Hero not found.")
        return

    for col in ["win_rate", "pick_rate", "ban_rate"]:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.replace("%", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    hero_cluster = int(selected.iloc[0]["cluster"])
    hero_rank = selected.iloc[0]["rank"]

    cluster_labels = {
        0: "Burst Damage Dealers",
        1: "Sustain Fighters (Lifesteal/Regen)",
        2: "Crowd-Control Supports",
        3: "Tank Frontliners (High Durability)",
        4: "Bruisers (Fighter-Assassin Hybrids)",
        5: "Basic Attack Marksmen",
        6: "Advanced / Mechanically Intensive Marksmen",
        7: "Mobile Skirmishers"
    }

    hero_cluster_label = cluster_labels.get(hero_cluster, "Unknown")

    feature_cols = [
        "defense_overall",
        "offense_overall",
        "skill_effect_overall",
        "difficulty_overall",
        "movement_spd",
    ]

    X = df[feature_cols].copy()

    scaler = MinMaxScaler(feature_range=(1, 10))
    X_scaled = scaler.fit_transform(X)

    skill_idx = feature_cols.index("skill_effect_overall")
    difficulty_idx = feature_cols.index("difficulty_overall")

    # Same feature scaling as original clustering
    X_scaled[:, skill_idx] *= 1.4
    X_scaled[:, difficulty_idx] *= 1.8

    hero_index = selected.index[0]

    distances = euclidean_distances(
        [X_scaled[hero_index]],
        X_scaled
    )[0]

    df["distance"] = distances

    # Filter same cluster
    recommendations = df[
        (df["cluster"] == hero_cluster) &
        (df["hero_name_clean"] != hero_name)
    ].copy()

    # Distance is the eucledian distance of one hero to another hero in the same cluster (lower distance means more similar)
    # Rank is chosen based on how well it ranks (Lower rank means better)
    # win_rate is how successful the hero is
    # pick_rate is chosen based on if the hero is currently popular (in meta)
    recommendations = recommendations.sort_values(
        by=["distance", "rank", "win_rate", "pick_rate"],
        ascending=[True, True, False, False]
    )

    top_5 = recommendations.head(5)
    top_2 = top_5.head(2)
    alternatives = top_5.iloc[2:5]

    print(f"\nHero entered: {selected.iloc[0]['hero_name']}")
    print(f"Cluster: {hero_cluster_label}")
    print(f"Rank: {hero_rank}")

    print("\nRecommended heroes based on similar playstyle and current meta:")
    for _, row in top_2.iterrows():
        print(f"- {row['hero_name']} | Rank: {row['rank']} | Win Rate: {row['win_rate']}% | Pick Rate: {row['pick_rate']}%")

    print("\nOther good hero choices:")
    for _, row in alternatives.iterrows():
        print(f"- {row['hero_name']} | Rank: {row['rank']} | Win Rate: {row['win_rate']}% | Pick Rate: {row['pick_rate']}%")

if __name__ == "__main__":
    recommend_heroes()