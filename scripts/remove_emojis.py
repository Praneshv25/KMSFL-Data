

import sqlite3
import re
import sys

def remove_emojis_and_strip(text):
    """
    Removes emoji characters from a string and strips leading/trailing whitespace.
    """
    if not text:
        return text
    
    # Regex to remove most common emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    
    # Remove emojis and then strip whitespace
    return emoji_pattern.sub(r"", text).strip()

def clean_table_column(cursor, table_name, column_name):
    """
    Removes emojis and strips whitespace from a specific column in a table.
    """
    print(f"Cleaning {table_name}.{column_name}...")
    
    try:
        cursor.execute(f"SELECT id, {column_name} FROM {table_name}")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"  Error reading from {table_name}.{column_name}: {e}")
        return 0

    updates_made = 0
    for row_id, text in rows:
        if text:
            cleaned_text = remove_emojis_and_strip(text)
            if cleaned_text != text:
                cursor.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE id = ?", (cleaned_text, row_id))
                updates_made += 1
    
    print(f"  - Found and fixed {updates_made} entries.")
    return updates_made

def main():
    """
    Main function to connect to the DB and clean all relevant team name fields.
    """
    db_path = '/Users/PV/PycharmProjects/FF DATA/data/espn_fantasy.db'
    print(f"Connecting to database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\nStarting database cleaning process...")
        
        # Clean teams table
        clean_table_column(cursor, 'teams', 'team_name')
        
        # Clean matchups table
        clean_table_column(cursor, 'matchups', 'home_team')
        clean_table_column(cursor, 'matchups', 'away_team')

        # Commit changes
        conn.commit()
        print("\nChanges committed to the database.")

    except sqlite3.Error as e:
        print(f"\nDatabase error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

    print("\nDatabase cleaning complete.")

if __name__ == "__main__":
    main()

