from flask import Blueprint, render_template, request, redirect, url_for, flash 
from flask_login import login_required, current_user
from . import players_bp

# View all players (accessible to everyone)
@players_bp.route('/', endpoint='view_players')
def view_players():
    return redirect('http://127.0.0.1:5001/players')


# Add a player (only for admins/coaches)
@players_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_player():
    
    
    if current_user.role not in ['admin', 'coach']:
        flash('Unauthorized access!', 'danger')
        return redirect('/players')

    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        height = request.form['height']
        weight = request.form['weight']
        player = Player(name=name, position=position, height=height, weight=weight)
        db.session.add(player)
        db.session.commit()
        flash('Player added successfully!', 'success')
        return redirect(url_for('players.view_players'))
    return render_template('add_player.html')

# Edit a player (only for admins/coaches)
#@players_bp.route('/edit/<int:player_id>', methods=['GET', 'POST'])
#@login_required
#def edit_player(player_id):
#    if current_user.role not in ['admin', 'coach']:
#        flash('Unauthorized access!', 'danger')
#        return redirect(url_for('/players'))
#      
#    from app import db
#    from models import Player
#    player = Player.query.get_or_404(player_id)
#    if request.method == 'POST':
#        player.name = request.form['name']
#        player.position = request.form['position']
#        player.height = request.form['height']
#        player.weight = request.form['weight']
#        db.session.commit()
#        flash('Player updated successfully!', 'success')
#        return redirect(url_for('players.view_players'))
#    return render_template('edit_player.html', player = player)

# Delete a player (only for admins/coaches)
@players_bp.route('/delete/<int:player_id>', methods=['POST'])
@login_required
def delete_player(player_id):
    if current_user.role not in ['admin', 'coach']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('players.view_players'))

    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    flash('Player deleted successfully!', 'success')
    return redirect(url_for('players.view_players'))
