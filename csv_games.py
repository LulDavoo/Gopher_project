import csv_helper
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app (but we won't run it)
app = Flask(__name__)

# Configure database 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://dnwankwo:Basketball1@localhost/dn_mygopher_db"
db = SQLAlchemy(app)

# Define models matching the database
class Players(db.Model):
    __tablename__ = "players"
    player_id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String, nullable=False)

class Games(db.Model):
    __tablename__ = "games"
    game_id = db.Column(db.Integer, primary_key=True)

# Load box score CSV (contains player names)
box_score_df = pd.read_csv("csv_games_with_names(allgames).csv") #change input to csv/excel

with app.app_context():
# Get player IDs from the database
    players_df = pd.read_sql("SELECT player_id, name FROM players", db.engine)
    print("Players DataFrame Columns:", players_df.columns.tolist())
    print(players_df.head())
     
    box_score_df = box_score_df[~box_score_df["Player"].isin(["STARTERS", "RESERVES", "ARTERS", "TALS", "nan", "TEAM", "SERVES", "", None])]
    box_score_df = box_score_df.dropna(subset=["Player"]) #Remove Nan
    box_score_df = box_score_df.applymap(lambda x: x.strip('"') if isinstance(x, str) else x)     
    # Print to show removal
    print("✅ Cleaned Box Score DataFrame:\n", box_score_df.head())
    
    # Convert numeric columns to integers if they don't need decimals
    numeric_columns = ["MIN", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "PTS"]

    for col in numeric_columns:
        box_score_df[col] = pd.to_numeric(box_score_df[col], errors="coerce").fillna(0).astype(int)  # Convert to numeric
        box_score_df[col] = box_score_df[col].astype("Int64")  # Convert to integer (keeping NaNs)

    # Check updated data types
    print("✅ Data Types After Conversion:\n", box_score_df.dtypes)

    # Make sure we're using the correct column for merging
    print("Box Score DataFrame Columns:\n", box_score_df.columns.tolist())
    
    # box_score_df = box_score_df[~box_score_df["Player"].isin(["STARTERS", "RESERVES"])]
    
    print("Available columns in box_score_df:\n", box_score_df.columns.tolist())
    # Print to confirm removal
    print("✅ Cleaned Box Score DataFrame:\n", box_score_df.head())

    # Change "Player" to the actual column name in the CSV
    player_column = None
    for col in box_score_df.columns:
        if "player" in col.lower():
            player_column = col
            break

    if player_column:
       print(f"Using column '{player_column}' as Player column")
       box_score_df = box_score_df.merge(players_df, left_on=player_column, right_on="name", how="left")
       print(players_df)
       print(box_score_df.head())
    else:
       print("❌ ERROR: No matching 'Player' column found in CSV!")
       print("Available columns:", box_score_df.columns.tolist())  # Debugging
       exit()

    # Assign the latest game_id to all rows
    #latest_game_id = db.session.execute(db.text("SELECT COALESCE(MAX(game_id), 0) + 1 FROM games")).fetchone()[0] #match game_id from input excel/csv
    #box_score_df["game_id"] = latest_game_id #see above

    # Merge game IDs into box score data
    games_df = pd.read_sql("SELECT game_id FROM games", db.engine)
    box_score_df = box_score_df.merge(games_df, on="game_id", how="left") #is this just adding game_id based off of the already existing game_id? if so that's not helpful

    # Drop unnecessary columns
    box_score_df.drop(columns=["name", "Player_and_number"], inplace=True, errors="ignore") #do you need?
    print(box_score_df.head())
    print(box_score_df)
    # Reorder columns to match the database
    column_order = ["game_id", "player_id", "Player", "MIN", "FGM-A", "3PM-A", "FTM-A", 
                    "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "PTS"]
    
    box_score_df = box_score_df[column_order]

    # Save the cleaned CSV
    box_score_df.to_csv("all_games_with_player_ids.csv", index=False) #change csv name to all_games_w_p_ids.csv or somehting similar
    print("✅ Updated CSV saved as 'all_games_with_player_ids.csv' with Player IDs and Game IDs.")

