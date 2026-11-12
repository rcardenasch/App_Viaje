from functools import wraps
from flask import jsonify
from flask_login import current_user


def error(mensaje, status=400):
    return jsonify(ok=False, mensaje=mensaje), status


def roles_requeridos(*roles):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return error("Debe iniciar sesión.", 401)
            if not current_user.activo:
                return error("La cuenta está desactivada.", 403)
            if current_user.rol not in roles:
                return error("No tiene permisos para esta operación.", 403)
            return func(*args, **kwargs)
        return wrapper
    return decorador


def es_admin():
    return current_user.is_authenticated and current_user.rol == "ADMINISTRADOR"
