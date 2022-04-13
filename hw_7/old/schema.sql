DROP TABLE IF EXISTS bibfiles;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  citation_tag TEXT UNIQUE NOT NULL,
  authors TEXT NOT NULL,
  journal TEXT NOT NULL,
  volume INTEGER,
  pages TEXT,
  year INTEGER,
  title TEXT NOT NULL,
  collection TEXT NOT NULL
);