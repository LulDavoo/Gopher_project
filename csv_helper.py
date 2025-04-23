import pandas as pd

def load_box_score(file_path):
    """Loads the box score CSV file into a DataFrame."""
    return pd.read_csv(file_path)

def merge_player_ids(box_score_df, db_engine):
    """Merges player IDs into the box score DataFrame."""
    players_df = pd.read_sql("SELECT player_id, player_name FROM players", db_engine)
    return box_score_df.merge(players_df, left_on="Player Name", right_on="player_name", how="left")

def merge_game_ids(box_score_df, db_engine):
    """Merges game IDs into the box score DataFrame."""
    games_df = pd.read_sql("SELECT game_id FROM games", db_engine)
    return box_score_df.merge(games_df, on="game_id", how="left")
