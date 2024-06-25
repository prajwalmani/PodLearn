import sqlite3

def create_database():
    """
    Creates a SQLite database 'podcast_episodes.db' and a table 'episodes' to store podcast episode details.
    """
    conn = sqlite3.connect('podcast_episodes.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS episodes (
        episode_id TEXT,
        audio_url TEXT,
        transcript TEXT
    )
''')
    
    print("Database created/initated successfully")
    conn.commit()
    conn.close()

def check_episode_exists(episode_id):
    """
    Checks if an episode exists in the SQLite database based on the provided episode_id.

    Args:
    - episode_id (str): The unique identifier of the episode to check.

    Returns:
    - str or None: The transcript of the episode if found, or None if the episode does not exist.
    """
    conn = sqlite3.connect('podcast_episodes.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM episodes WHERE episode_id = ?', (episode_id,))
    row = cursor.fetchone()

    conn.commit()
    conn.close()

    if row:
        return row
    else:
        return None
    
def insert_episode(episode_id, audio_url, transcript):
    """
    Inserts a new episode into the 'episodes' table of the SQLite database.

    Args:
    - episode_id (str): The unique identifier of the episode.
    - audio_url (str): The URL of the audio for the episode.
    - transcript (str): The transcript of the episode.

    Returns:
    - bool: True if insertion is successful, False otherwise.
    """
    conn = sqlite3.connect('podcast_episodes.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO episodes (episode_id, audio_url, transcript)
        VALUES (?, ?, ?)
    ''', (episode_id, audio_url, transcript))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Episode with ID '{episode_id}' inserted successfully.")

def clear_table():
    """
    Clears all rows from the 'episodes' table in the SQLite database.
    """
    conn = sqlite3.connect('podcast_episodes.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM episodes')
    
    conn.commit()

    cursor.close()
    conn.close()

    print("Table 'episodes' cleared successfully.")
# clear_table()


