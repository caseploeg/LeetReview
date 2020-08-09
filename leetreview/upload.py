import os
import json
import sqlite3
from flask import Blueprint, g, render_template, send_from_directory, flash, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename

from leetreview.auth import login_required
from leetreview.db import get_db


ALLOWED_EXTENSIONS = {'py'}
bp = Blueprint('upload', __name__, url_prefix='/upload')

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        url = request.form["url"]
        id = request.form["id"]
        current_app.logger.info(url)
        file = request.files['file']
        # if user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if id == '':
            flash('No id given')
            return redirect(request.url)
        # check id is unique
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            lines = []
            for line in file.stream:
                # need to decode the input as utf-8, so this
                # is a requirement for file format
                line = line.rstrip().decode("utf-8")
                # ignoring blank lines / purely whitespace
                if line:
                    lines.append(line)
            obj = json.dumps(lines)

            # if the file wasn't completely new lines / whitespace
            # create a entry in the database
            if len(lines) != 0:
                db = get_db()
                try:
                    db.execute(
                        'INSERT INTO solution (id, lines, author_id, original_url)'
                        ' VALUES (?, ?, ?, ?)',
                        (id, obj, g.user['id'], url)
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    flash('id not unique')
                    return redirect(request.url)
                return redirect(url_for('upload.uploaded_file', filename=filename))
                # return redirect(url_for('index'))
            else:
                flash('Empty File')
    return render_template('upload/index.html')


@bp.route('<path:filename>')
def uploaded_file(filename):
    db = get_db()
    solutions = db.execute(
        'SELECT s.id, lines, created, author_id, original_url'
        ' FROM solution s JOIN user u ON s.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    current_app.logger.info(solutions)
    return render_template('upload/solutions.html', solutions=solutions)
    # return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
