import json

from flask import (
            Blueprint, flash, g, redirect, render_template, request, url_for, current_app
            )
from werkzeug.exceptions import abort

from leetreview.auth import login_required
from leetreview.db import get_db

bp = Blueprint('solutions', __name__, url_prefix='/solutions')


def get_solution(id):
    # select the solution from the database with matching id
    db = get_db()
    solution = db.execute(
        'SELECT s.id, lines, created, author_id, original_url'
        ' FROM solution s JOIN user u ON s.author_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()
    return solution


@bp.route('/')
def index():
    db = get_db()
    # grabs all uploaded solutions, regardless of user
    solutions = db.execute(
        'SELECT s.id, lines, created, author_id, original_url'
        ' FROM solution s JOIN user u ON s.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('solutions/index.html', solutions=solutions)


# takes a json formatted string representing the lines of code
# for a solution, and returns the new line seperated version of the
# string for display purposes in templates
def get_display_lines(lines):
    lines = '\n'.join(json.loads(lines))
    return lines 


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    solution = get_solution(id)

    print(solution)
    if request.method == 'POST':
        lines = request.form['lines']
        lines = json.dumps(lines.split('\n'))
        print(lines)
        db = get_db()
        db.execute(
            'UPDATE solution SET lines = ?'
            ' WHERE id = ?',
            (lines, id)
        )
        db.commit()
        return redirect(url_for('solutions.index'))
    return render_template('solutions/edit.html', s=solution, get_lines=get_display_lines) 


@bp.route('/<id>/merge', methods=('GET', 'POST'))
def merge(id):
    solution = get_solution(id)
    if request.method == 'POST':
        lines = request.get_json()
        lines = json.dumps(lines)
        db = get_db()
        db.execute(
            'UPDATE solution SET lines = ?'
            ' WHERE id = ?',
            (lines, id)
        )
        db.commit()
        return redirect(url_for('solutions.index'))
    else:
        lines = json.loads(solution["lines"])
        return render_template('solutions/merge.html', s=solution, lines=lines)


