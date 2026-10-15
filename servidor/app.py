"""API REST de gestión de tareas (Flask + SQLite)."""
import os

from flask import Flask, g, jsonify, render_template, request, session

from . import db
from .auth import login_requerido
from .repositorios import TareaRepositorio, UsuarioRepositorio

app = Flask(__name__)
# En producción definí SECRET_KEY como variable de entorno.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")
db.init_app(app)


def _credenciales():
    """Extrae y valida usuario/contraseña del JSON. Devuelve (usuario, pass, error)."""
    datos = request.get_json(silent=True) or {}
    usuario = str(datos.get("usuario", "")).strip()
    contrasena = str(datos.get("contraseña", ""))
    if not usuario or not contrasena:
        return None, None, "Usuario y contraseña son obligatorios"
    if len(contrasena) < 6:
        return None, None, "La contraseña debe tener al menos 6 caracteres"
    return usuario, contrasena, None


@app.post("/registro")
def registro():
    usuario, contrasena, error = _credenciales()
    if error:
        return jsonify({"error": error}), 400
    if UsuarioRepositorio().crear(usuario, contrasena) is None:
        return jsonify({"error": "El usuario ya existe"}), 409
    return jsonify({"mensaje": "Usuario registrado"}), 201


@app.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    usuario = str(datos.get("usuario", "")).strip()
    contrasena = str(datos.get("contraseña", ""))
    usuario_id = UsuarioRepositorio().verificar(usuario, contrasena)
    if usuario_id is None:
        return jsonify({"error": "Credenciales inválidas"}), 401
    session.clear()
    session["usuario_id"] = usuario_id
    return jsonify({"mensaje": "Sesión iniciada"}), 200


@app.post("/logout")
@login_requerido
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada"}), 200


@app.get("/tareas")
@login_requerido
def tareas_html():
    tareas = TareaRepositorio().listar(g.usuario["id"])
    return render_template("tareas.html", usuario=g.usuario["usuario"], tareas=tareas)


@app.get("/api/tareas")
@login_requerido
def api_listar():
    return jsonify(TareaRepositorio().listar(g.usuario["id"])), 200


@app.post("/api/tareas")
@login_requerido
def api_crear():
    datos = request.get_json(silent=True) or {}
    titulo = str(datos.get("titulo", "")).strip()
    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    tarea = TareaRepositorio().crear(g.usuario["id"], titulo)
    return jsonify(tarea), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
