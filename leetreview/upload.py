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


def get_id(name):
    return name.rsplit('.', 1)[0].lower()


def get_url(id):
    return "https://leetcode.com/problems/" + id


def upload(file, id=None, url=None):
    if file.filename == '':
        flash('No selected file')
        return False 
    if not id:
        id = get_id(file.filename)
    if not url:
        url = get_url(id)
    if id == '':
        flash('No id given')
        return False
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
                flash('id not unique ' + id)
                return False 
            return True
        else:
            flash('Empty File')
            return False
    return False

@bp.route('/fast/', methods=['GET', 'POST'])
@login_required
def fast_upload():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        success = True
        for f in uploaded_files: 
            # make sure call to upload is first to avoid lazy evaluation
            success = upload(f) and success
        if not success:
            return redirect(request.url)
        else:
            return redirect(url_for('solutions.index'))
    return render_template('upload/fast.html')


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
        file = request.files['file']
        # if user does not select file, browser also
        # submits an empty part without filename
        success = upload(file, id, url)
        if not success:
            return redirect(request.url)
        else:
            return redirect(url_for('solutions.index'))
    return render_template('upload/index.html')
