from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import games_bp  # Import the Blueprint from __init__.py



# View all games
@games_bp.route('/')
def view_games():
    from app import Game
    from app import db
    return redirect('http://127.0.0.1:5001/games')
    
    

# Add a new game
@games_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_game():
    if current_user.role not in ['admin', 'coach']:
        flash("Unauthorized", 'danger')
        return redirect(url_for('games.view_games'))

    if request.method == 'POST':
        # Example fields
        opponent = request.form['opponent']
        date = request.form['date']
        location = request.form['location']
        new_game = Game(opponent=opponent, date=date, location=location)
        db.session.add(new_game)
        db.session.commit()
        flash("Game added!", 'success')
        return redirect(url_for('games.view_games'))

    return render_template('add_game.html')

# Edit a game
#@games_bp.route('/edit/<int:game_id>', methods=['GET', 'POST'])
#@login_required
#def edit_game(game_id):
#    if current_user.role not in ['admin', 'coach']:
#          flash("Unauthorized", 'danger')
#          return redirect(url_for('/games'))
#    from app import Game
#    game = Game.query.get_or_404(game_id)
    
#    if request.method == 'POST':
#          game.opponent = request.form['opponent']
#          game.date = request.form['date']
#          game.location = request.form['location']
#          db.session.commit()
#          flash("Game updated!", 'success')
#          return redirect(url_for('games.view_games'))

#    return render_template('edit_game.html', game=game)

# Delete a game
@games_bp.route('/delete/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    if current_user.role not in ['admin', 'coach']:
        flash("Unauthorized", 'danger')
        return redirect(url_for('games.view_games'))

    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    flash("Game deleted!", 'success')
    return redirect(url_for('games.view_games'))
