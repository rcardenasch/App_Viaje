from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from modelos import db
from modelos.ubicacion import Ubicacion
from rutas._comun import error, roles_requeridos

ubicaciones_bp = Blueprint("ubicaciones", __name__, url_prefix="/ubicaciones")


def serializar(u):
    return {"id_ubicacion": u.id_ubicacion, "nombre": u.nombre,
            "departamento": u.departamento, "provincia": u.provincia,
            "distrito": u.distrito, "referencia": u.referencia,
            "activo": u.activo, "nombre_completo": u.nombre_completo}


def validar(data):
    campos = {"nombre": 150, "departamento": 100, "provincia": 100, "distrito": 100}
    valores = {k: str(data.get(k, "")).strip() for k in campos}
    if any(not valores[k] for k in campos):
        return None, "Nombre, departamento, provincia y distrito son obligatorios."
    if any(len(valores[k]) > limite for k, limite in campos.items()):
        return None, "Uno o más campos exceden su longitud máxima."
    referencia = str(data.get("referencia") or "").strip() or None
    if referencia and len(referencia) > 250:
        return None, "La referencia no puede superar 250 caracteres."
    valores["referencia"] = referencia
    return valores, None


@ubicaciones_bp.get("/")
def listar():
    q = Ubicacion.query
    texto = request.args.get("q", "").strip()
    if texto:
        patron = f"%{texto}%"
        q = q.filter(or_(Ubicacion.nombre.ilike(patron),
                         Ubicacion.departamento.ilike(patron),
                         Ubicacion.provincia.ilike(patron),
                         Ubicacion.distrito.ilike(patron)))
    if request.args.get("incluir_inactivas") != "1":
        q = q.filter(Ubicacion.activo.is_(True))
    datos = q.order_by(Ubicacion.departamento, Ubicacion.provincia,
                       Ubicacion.distrito, Ubicacion.nombre).all()
    return jsonify(ok=True, datos=[serializar(x) for x in datos])


@ubicaciones_bp.get("/<int:id_ubicacion>")
def obtener(id_ubicacion):
    u = db.session.get(Ubicacion, id_ubicacion)
    if not u:
        return error("Ubicación no encontrada.", 404)
    return jsonify(ok=True, dato=serializar(u))


@ubicaciones_bp.post("/")
@roles_requeridos("ADMINISTRADOR")
def crear():
    valores, mensaje = validar(request.get_json(silent=True) or request.form)
    if mensaje:
        return error(mensaje)
    u = Ubicacion(**valores)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe esa ubicación.", 409)
    return jsonify(ok=True, mensaje="Ubicación creada.", dato=serializar(u)), 201


@ubicaciones_bp.put("/<int:id_ubicacion>")
@roles_requeridos("ADMINISTRADOR")
def editar(id_ubicacion):
    u = db.session.get(Ubicacion, id_ubicacion)
    if not u:
        return error("Ubicación no encontrada.", 404)
    valores, mensaje = validar(request.get_json(silent=True) or request.form)
    if mensaje:
        return error(mensaje)
    for campo, valor in valores.items():
        setattr(u, campo, valor)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe otra ubicación con esos datos.", 409)
    return jsonify(ok=True, mensaje="Ubicación actualizada.", dato=serializar(u))


@ubicaciones_bp.patch("/<int:id_ubicacion>/estado")
@roles_requeridos("ADMINISTRADOR")
def cambiar_estado(id_ubicacion):
    u = db.session.get(Ubicacion, id_ubicacion)
    if not u:
        return error("Ubicación no encontrada.", 404)
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("activo"), bool):
        return error("El campo activo debe ser booleano.")
    u.activo = data["activo"]
    db.session.commit()
    return jsonify(ok=True, activo=u.activo)
