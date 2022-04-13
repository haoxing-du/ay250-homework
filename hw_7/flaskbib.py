import os
from flask import Flask, flash, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import pybtex
from pybtex.plugin import find_plugin
from pybtex.database import parse_file

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'bib'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_path = "db.sqlite3"

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    create table if not exists bib (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_tag TEXT UNIQUE NOT NULL,
        author_list TEXT NOT NULL,
        journal TEXT NOT NULL,
        volume INTEGER,
        pages TEXT,
        year INTEGER,
        title TEXT NOT NULL,
        collection TEXT NOT NULL
    );
""")
conn.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pybtex_parser(filename, collection_name):
    data = parse_file(filename, 'bibtex')
    data_lower = data.lower()
    for entry in data_lower.entries.values():
        ref_tag = entry.key
        authors = entry.persons['author']
        author_list = []
        for author in authors:
            first_names = ' '.join(author.first_names)
            last_names = ' '.join(author.last_names)
            middle_names = ' '.join(author.middle_names)
            author_str = last_names + ', ' + first_names + ' ' + middle_names
            author_list.append(author_str)

        title = entry.fields['title']

        if 'journal' in entry.fields.keys():
            journal = entry.fields['journal']
        else:
            journal = None

        if 'volume' in entry.fields.keys():
            volume = int(entry.fields['volume'])
        else:
            volume = None

        if 'pages' in entry.fields.keys():
            pages = entry.fields['pages']
        else:
            pages = None

        if 'year' in entry.fields.keys():
            year = int(entry.fields['year'])
        else:
            year = None

        if 'volume' in entry.fields.keys():
            volume = entry.fields['volume']
        else:
            volume = None
        
        cursor.execute(f"insert into bib (ref_tag) values ({ref_tag})")
        
    return ""

@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        
            return redirect(request.url)

    return render_template("home.html")

@app.route('/insert_collection', methods=['GET', 'POST'])
def insert_collection():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        collection_name = request.form['name']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_name_and_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_name_and_path)
            cmd = pybtex_parser(file_name_and_path, collection_name)

            return redirect(request.url)
            #return redirect(url_for('download_file', name=filename))

    return render_template("upload.html")

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        query = request.form['query']
        return redirect(request.url)

    return render_template("query.html")

if __name__ == "__main__":
    app.run()