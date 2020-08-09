import json
import random


from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, url_for, current_app
)

from leetreview.auth import login_required
from leetreview.db import get_db

bp = Blueprint('practice', __name__, url_prefix='/practice')

@bp.route('/check', methods=['POST'])
def check_answer():
    # receives the users answer to the scrambled code, for a specified solution / id
    # and returns whether the submitted permutation is correct or not
    if request.method == 'POST':
        req_json = request.get_json()
        id = req_json['id']
        db = get_db()
        # select the solution from the database with matching id
        solution = db.execute(
            'SELECT s.id, lines, created, author_id'
            ' FROM solution s JOIN user u ON s.author_id = u.id'
            ' WHERE s.id = ?',
            (id,)
        ).fetchone()

        saved_lines = json.loads(solution["lines"]) 
        user_lines = req_json['lines']
        correct = True

        # check for equality between the saved answer and the submitted one
        for l1, l2 in zip(user_lines, saved_lines):
            current_app.logger.info(l1)
            current_app.logger.info(l2)
            if l1 != l2:
                correct = False
                break

        # return whether the answer was correct or not in the request
        return jsonify(correct) 


@bp.route('/')
@login_required
def index():
    db = get_db()
    solutions = db.execute(
        'SELECT s.id, lines, created, author_id, original_url'
        ' FROM solution s JOIN user u ON s.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    solution = random.choice(solutions)
    current_app.logger.info(solution)
    saved_lines = json.loads(solution["lines"]) 
    shuffled_lines = random.sample(saved_lines, k=len(saved_lines)) 

    # setting default to str fixes issues with dates and other objects not being serializable.
    # rows are converted to tuples from the SQLite.Row type in order to serializable.
    # solutions = json.dumps([tuple(row) for row in solutions], indent=4, default=str)

    # For now just send the shuffled lines to the practice page.
    # In the future, other data will need to be sent so the client can send solutions
    # back to the server 
    return render_template('practice/index.html', lines=shuffled_lines, url=solution['original_url'], id=solution['id'])
