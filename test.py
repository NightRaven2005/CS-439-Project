import sqlite3

def main():
    conn = sqlite3.connect("mlbb_database.db")  # change to your DB file
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clustered_hero_stats")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    main()