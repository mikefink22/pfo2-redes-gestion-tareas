"""Conexión a SQLite y creación de tablas.

El archivo de la base de datos (tareas.db) se crea SOLO la primera vez que
arranca el servidor. Queda dentro de la carpeta servidor/ y está en .gitignore,
por lo que no se sube a GitHub.
"""
import os
import sqlite3

from flask import g

# Ruta del archivo .db (se puede cambiar con la variable de entorno DB_PATH)
DB_PATH = os.environ.get(
    "DB_PATH", os.path.join(os.path.dirname(__file__), "tareas.db")
)

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    completada INTEGER NOT NULL DEFAULT 0,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
"""


def get_db():
    """Devuelve la conexión de la request actual (una por request)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas si no existen."""
    conexion = sqlite3.connect(DB_PATH)
    conexion.executescript(ESQUEMA)
    conexion.commit()
    conexion.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    init_db()
