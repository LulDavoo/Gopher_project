from sqlalchemy import text
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_login import LoginManager, login_user, logout_user
from flask_login import login_required, current_user
from flask_login import UserMixin


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey123'

# Configure the PostgreSQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dnwankwo:Basketball1@localhost/dn_mygopher_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize SQLAlchemy
db = SQLAlchemy()
print("Call SQLAlchemy once")
#db.app = app
with app.app_context():
    from players import players_bp
    
    db.init_app(app)
    
    app.register_blueprint(players_bp, url_prefix='/players')
    
    from games import games_bp
    app.register_blueprint(games_bp, url_prefix='/games')
    
    db.create_all()

print("That db.init_app is being called")
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

# After login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Coach.query.get(int(user_id))


# Define the Coaches table
class Coach(db.Model, UserMixin):
    __tablename__ ='coaches'
    coach_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    email = db.Column(db.String(100))
    image_url = db.Column(db.String(200))   #This will store image URL's

    def get_id(self):
        return str(self.coach_id)
        
    # Defining Players table
class Player(db.Model):
    __tablename__ = 'players'
    player_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    jersey_number = db.Column(db.Integer)
    position = db.Column(db.String(50))
    height = db.Column(db.String(20))
    weight = db.Column(db.Integer)
    class_year = db.Column(db.String(20))
    image_url = db.Column(db.String(200))      #This will store image URL's
    major = db.Column(db.Text, nullable=False)
    minor = db.Column(db.Text, nullable=True)

class Game(db.Model):
    __tablename__ = 'games'  # Name of the table in the database
    game_id = db.Column(db.Integer, primary_key=True)  
    opponent = db.Column(db.String(100), nullable=False)  
    goucher_score = db.Column(db.Integer, nullable=False)  
    opponent_score = db.Column(db.Integer, nullable=False)  
    home_or_away = db.Column(db.String(10), nullable=False)  
    season = db.Column(db.String(9), nullable=False)  # Season (e.g., "2023-2024")
    game_date = db.Column(db.Date, nullable=False)  # Date of the game
    result = db.Column(db.String(10), nullable=False)  # Result ( "Win" or "Loss")

@app.route('/coaches')
def coaches():
    # Query the database for all coaches
    coaches = Coach.query.filter(Coach.role != 'admin').all()
    
    # Render the template, passing the users data to be displayed
    return render_template('index.html', coaches= coaches)

@app.route('/players')
def players():
    players = Player.query.all()  #Retrieve all players
    players = Player.query.order_by(Player.player_id).all()
    return render_template('players.html', players=players)

@app.route('/player/<int:player_id>')
def player_profile(player_id):
    # Query player details
    player = Player.query.filter_by(player_id=player_id).first()

    # Query all game stats for the specific player
    stats = db.session.execute(text("""
    SELECT games_played, points_per_game, fg_pct, three_pt_pct, ft_pct, reb_per_game, ast_per_game 
    FROM season_stats WHERE player_id = :player_id
"""), {"player_id": player_id}).fetchone()


    if not player:
        return "Player not found", 404

    return render_template('player_profile.html', player=player, stats=stats)

@app.route('/games')
def games():
    games = Game.query.order_by(Game.game_id).all()  #Order by game_id

    # Calculate overall stats 
    overall = "10-16"
    pct = .385
    conf = "8-10"
    cpct = .444
    streak = "L1"
    home = "7-5" 
    away = "3-11"
    neutral = "0-0"
    streak = "L1"
    neutral = "0-0"
    return render_template('games.html', games=games, overall=overall, pct=pct, conf=conf, cpct=cpct, streak=streak,home=home, away=away, neutral=neutral)
   
@app.route('/boxscore/<int:game_id>')
def boxscore(game_id):
    box_score_df = pd.read_csv("all_games_with_player_ids.csv") #change to all names w player ids

    

    # Debug: Print the filtered DataFrame
    print("CSV Columns:", box_score_df.columns.tolist())

    # Print first few rows
    print(box_score_df.head())

    if "player_id" not in box_score_df.columns:
        return "Error: 'player_id' column not found in CSV", 500
   
    #print("Available Game IDs:", box_score_df["game_id"].unique())

    if game_id not in box_score_df["game_id"].values:
        return f"No data found for game {game_id}", 404

    # Convert DataFrame to dictionary for Jinja
    game_box_score = box_score_df[box_score_df["game_id"]  == game_id]
    box_scores = game_box_score.to_dict(orient="records")  
    stats = db.session.execute(text(""" SELECT players.name, minutes_played, "fgm-a","3pm-a", "ftm-a", oreb, dreb, rebounds, ast, blk, turnovers, personal_fouls, pts FROM player_game_stats JOIN players ON player_game_stats.player_id = players.player_id
    WHERE game_id = :game_id;
    """), {"game_id": game_id}). fetchall()
     
    totals = {
        "FGM": game_box_score["FGM-A"].astype(str).apply(lambda x: int(x.split('-')[0])).sum(),
        "FGA": game_box_score["FGM-A"].astype(str).apply(lambda x: int(x.split('-')[1])).sum(),
        "3PM": game_box_score["3PM-A"].astype(str).apply(lambda x: int(x.split('-')[0])).sum(),
        "3PA": game_box_score["3PM-A"].astype(str).apply(lambda x: int(x.split('-')[1])).sum(),
        "FTM": game_box_score["FTM-A"].astype(str).apply(lambda x: int(x.split('-')[0])).sum(),
        "FTA": game_box_score["FTM-A"].astype(str).apply(lambda x: int(x.split('-')[1])).sum(),
        "OREB": game_box_score["OREB"].sum(),
        "DREB": game_box_score["DREB"].sum(),
        "REB": game_box_score["REB"].sum(),
        "AST": game_box_score["AST"].sum(),
        "STL": game_box_score["STL"].sum(),
        "BLK": game_box_score["BLK"].sum(),
        "TO": game_box_score["TO"].sum(),
        "PF": game_box_score["PF"].sum(),
        "PTS": game_box_score["PTS"].sum(),
    }

    totals["FG%"] = round((totals["FGM"] / totals["FGA"]) * 100, 1) if totals["FGA"] > 0 else 0
    totals["3P%"] = round((totals["3PM"] / totals["3PA"]) * 100, 1) if totals["3PA"] > 0 else 0
    totals["FT%"] = round((totals["FTM"] / totals["FTA"]) * 100, 1) if totals["FTA"] > 0 else 0
    print("Totals Data:", totals)
   
    return render_template('boxscore.html', box_scores=box_scores, stats=stats, game_id=game_id, totals=totals)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        coach = Coach.query.filter_by(email=email).first()

        if coach:
            login_user(coach)
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('players.add_player'))
        else:
            flash('Invalid email.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()  # logs out the user from Flask-Login
    session.pop('logged_in', None)  # remove session flag
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))  # send them to home 

@app.route('/players/edit/<int:player_id>', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    if current_user.role not in ['admin', 'coach']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('/players'))
        
    player = Player.query.get_or_404(player_id)
    if request.method == 'POST':
        player.name = request.form['name']
        player.position = request.form['position']
        player.height = request.form['height']
        player.weight = request.form['weight']
        db.session.commit()
        flash('Player updated successfully!', 'success')
        return redirect('http://127.0.0.1:5001/players')
    return render_template('edit_player.html', player = player)
    
@app.route('/games/edit/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    if current_user.role not in ['admin', 'coach']:
          flash("Unauthorized", 'danger')
          return redirect(url_for('/games'))
    
    game = Game.query.get_or_404(game_id)
    if request.method == 'POST':
           game.opponent = request.form['opponent']
           game.date = request.form['date']
           game.location = request.form['location']
           db.session.commit()
           flash("Game updated!", 'success')
           return redirect(url_for('games.edit_game', game_id=game.id))

    return render_template('edit_game.html', game=game)

@app.route('/')
def home():
    return render_template('home.html')
    


@app.context_processor
def inject_user():
    return dict(session=session)

if __name__ == "__main__": 
   app.run(debug=True, port=5001)

