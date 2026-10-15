"""Decorador de autenticación basado en la sesión (cookie firmada de Flask)."""
from functools import wraps

from flask import g, jsonify, session

from .repositorios import UsuarioRepositorio


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        usuario_id = session.get("usuario_id")
        usuario = UsuarioRepositorio().obtener(usuario_id) if usuario_id else None
        if usuario is None:
            session.clear()
            return jsonify({"error": "No autenticado"}), 401
        g.usuario = usuario
        return vista(*args, **kwargs)

    return envoltura
