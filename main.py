import pandas as pd
import sqlite3
from cluster import run_clustering
from recommend import recommend_heroes

def main():
    # 3 names had to be slightly modified in mlbb_heroes.csv due to inconsistency in naming between the 2 datasets
    df1 = pd.read_csv("mobile_legends_rank_stats.csv")
    df2 = pd.read_csv("mlbb_heros.csv") 

    # These columns are dropped as they are either outdated (the 3 rates) or serve no purpose (release_year)
    df2 = df2.drop(columns=["win_rate", "pick_rate", "ban_rate", "release_year"])

    conn = sqlite3.connect("mlbb_database.db")

    df1.to_sql("rank_stats", conn, if_exists="replace", index=False)
    df2.to_sql("heroes", conn, if_exists="replace", index=False)

    conn.execute("UPDATE heroes SET hero_name = LOWER(TRIM(hero_name));")
    conn.execute("UPDATE rank_stats SET hero = LOWER(TRIM(hero));")

    conn.execute("DROP TABLE IF EXISTS hero_stats;")

    query = """
    CREATE TABLE hero_stats AS
    SELECT h.*, r.rank, r.pick_rate, r.win_rate, r.ban_rate
    FROM heroes h
    LEFT JOIN rank_stats r
    ON h.hero_name = r.hero;
    """

    conn.execute(query)
    conn.commit()
    conn.close()

    run_clustering() # Runs the clustering algo and returns the results in a table inside the db

    recommend_heroes() # Runs the recommondation algo and return 5 heroes similar to the user inputted choice

if __name__ == "__main__":
    main()