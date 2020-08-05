import json
import random


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)

from leetreview.auth import login_required
from leetreview.db import get_db

bp = Blueprint('practice', __name__, url_prefix='/practice')

@bp.route('/')
@login_required
def index():
    db = get_db()
    solution = db.execute(
        'SELECT s.id, lines, created, author_id'
        ' FROM solution s JOIN user u ON s.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchone()
    current_app.logger.info(solution)
    saved_lines = json.loads(solution["lines"]) 
    shuffled_lines = random.sample(saved_lines, k=len(saved_lines)) 

    # setting default to str fixes issues with dates and other objects not being serializable.
    # rows are converted to tuples from the SQLite.Row type in order to serializable.
    # solutions = json.dumps([tuple(row) for row in solutions], indent=4, default=str)

    # For now just send the shuffled lines to the practice page.
    # In the future, other data will need to be sent so the client can send solutions
    # back to the server 
    return render_template('practice/index.html', lines=shuffled_lines)
