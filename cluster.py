import pandas as pd
import sqlite3
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

def run_clustering():
    conn = sqlite3.connect("mlbb_database.db")

    df = pd.read_sql_query("SELECT * FROM hero_stats", conn)
    conn.close()

    feature_cols = [
        "defense_overall",
        "offense_overall",
        "skill_effect_overall",
        "difficulty_overall",
        "movement_spd"
    ]

    X_numeric = df[feature_cols].copy()

    # Scale numeric features to 1–10
    scaler = MinMaxScaler(feature_range=(1, 10))
    X_numeric_scaled = scaler.fit_transform(X_numeric)

    X_numeric_scaled = pd.DataFrame(
        X_numeric_scaled,
        columns=feature_cols,
        index=df.index
    )

    # Give difficulty more importance
    X_numeric_scaled["difficulty_overall"] *= 1.5 # Ensures high difficulty heroes are only given to people who already know some hight difficulty hero already as some of these heroes if not used properly are kind of pointless to use

    # One-hot encode role and give role weight
    role_encoded = pd.get_dummies(df["role"], prefix="role")
    role_encoded = role_encoded * 1.2 # This makes the role behave more like a light guiding feature rather than the clustering just depending dominantly on it

    # Combine numeric + role features
    X_final = pd.concat([X_numeric_scaled, role_encoded], axis=1)

    # K-means clustering
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_final)

    # Evaluation of how well we clustered
    score = silhouette_score(X_final, kmeans.labels_) 
    print("Silhouette Score:", score)

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_final)

    # Plot clusters
    plt.figure(figsize=(10, 7))

    scatter = plt.scatter(
        pca_result[:, 0],
        pca_result[:, 1],
        c=kmeans.labels_
    )

    plt.title("PCA Projection of Hero Clusters")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")

    plt.colorbar(scatter)
    plt.show()

    conn = sqlite3.connect("mlbb_database.db")
    df.to_sql("clustered_hero_stats", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_clustering()
