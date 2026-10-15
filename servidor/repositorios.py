"""Patrón Repositorio: todo el SQL vive acá, el resto de la app no lo ve."""
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db


class UsuarioRepositorio:
    def crear(self, usuario, contrasena):
        """Crea un usuario con contraseña hasheada (scrypt + salt aleatorio).

        Devuelve el id nuevo, o None si el usuario ya existe.
        """
        hash_ = generate_password_hash(contrasena, method="scrypt")
        db = get_db()
        try:
            cur = db.execute(
                "INSERT INTO usuarios (usuario, contrasena_hash) VALUES (?, ?)",
                (usuario, hash_),
            )
            db.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def verificar(self, usuario, contrasena):
        """Devuelve el id si las credenciales son válidas, si no None."""
        fila = get_db().execute(
            "SELECT id, contrasena_hash FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()
        if fila and check_password_hash(fila["contrasena_hash"], contrasena):
            return fila["id"]
        return None

    def obtener(self, usuario_id):
        return get_db().execute(
            "SELECT id, usuario FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()


class TareaRepositorio:
    def listar(self, usuario_id):
        filas = get_db().execute(
            "SELECT id, titulo, completada FROM tareas "
            "WHERE usuario_id = ? ORDER BY id",
            (usuario_id,),
        ).fetchall()
        return [dict(f) for f in filas]

    def crear(self, usuario_id, titulo):
        db = get_db()
        cur = db.execute(
            "INSERT INTO tareas (titulo, usuario_id) VALUES (?, ?)",
            (titulo, usuario_id),
        )
        db.commit()
        return {"id": cur.lastrowid, "titulo": titulo, "completada": 0}
