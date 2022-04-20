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
        author_list TEXT,
        journal TEXT,
        volume INTEGER,
        pages TEXT,
        year INTEGER,
        title TEXT,
        collection TEXT
    );
""")
cursor.execute("delete from bib;")
conn.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pybtex_parser(filename, collection):
    data = parse_file(filename, 'bibtex')
    data_lower = data.lower()
    for entry in data_lower.entries.values():
        ref_tag = entry.key
        authors = entry.persons['author'] if 'author' in entry.persons else None
        author_list = []
        if authors is not None:
            for author in authors:
                first_names = ' '.join(author.first_names)
                last_names = ' '.join(author.last_names)
                middle_names = ' '.join(author.middle_names)
                author_str = last_names + ', ' + first_names + ' ' + middle_names
                author_list.append(author_str)
        
        author_list_str = ','.join(author_list)

        title = entry.fields['title']

        journal = entry.fields.get('journal')
        pages = entry.fields.get('pages')
        volume = int(entry.fields['volume']) if "volume" in entry.fields else None
        year = int(entry.fields['year']) if "year" in entry.fields else None
        
        cmd = "insert into bib (ref_tag, author_list, journal, volume," + \
              "pages, year, title, collection) values (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(cmd, (ref_tag, author_list_str, journal, volume,
                             pages, year, title, collection))
        conn.commit()
    return

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
        collection = request.form['name']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_name_and_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_name_and_path)
            pybtex_parser(file_name_and_path, collection)        

            return redirect(request.url)
    
    cursor.execute('select distinct collection from bib')
    output = cursor.fetchall()
    collections = [elem[0] for elem in output]
    return render_template("upload.html", collections=collections)

@app.route('/query', methods=['GET'])
def query():
    query = request.args.get("query")
    if query is None:
        return render_template("query.html")
    cmd = 'select * from bib where ' + query
    cursor.execute(cmd)
    output = cursor.fetchall()
    return render_template("query.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)