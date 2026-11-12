from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_login import current_user
from modelos import db
from modelos.usuario import Usuario
from modelos.propietario import Propietario
from modelos.vehiculo import Vehiculo
from modelos.plantilla_asientos import PlantillaAsientos
from modelos.asiento import Asiento
from rutas._comun import error, roles_requeridos, es_admin

vehiculos_bp = Blueprint("vehiculos", __name__, url_prefix="/vehiculos")
TIPOS = {"AUTO", "VAN", "MINIBUS", "BUS", "OTRO"}


def serializar(v):
    return {"id_vehiculo": v.id_vehiculo, "id_propietario": v.id_propietario,
            "id_plantilla": v.id_plantilla, "placa": v.placa,
            "marca": v.marca, "modelo": v.modelo, "tipo": v.tipo,
            "cantidad_asientos": v.cantidad_asientos, "activo": v.activo}


def puede_operar(v):
    return es_admin() or v.id_propietario == current_user.id_usuario


def generar_asientos(v, plantilla, reemplazar=False):
    matriz = plantilla.distribucion
    if not isinstance(matriz, list):
        raise ValueError("La distribución de asientos debe ser una matriz.")
    if v.asientos and not reemplazar:
        return
    if reemplazar:
        if any(a.reservas for a in v.asientos):
            raise ValueError("No se puede regenerar la distribución: existen reservas asociadas.")
        v.asientos.clear()
        db.session.flush()
    nuevos, vistos = [], set()
    for fila_idx, fila in enumerate(matriz, 1):
        if not isinstance(fila, list):
            raise ValueError("Cada fila de la distribución debe ser una lista.")
        for col_idx, valor in enumerate(fila, 1):
            if valor is None or str(valor).strip().upper() in {"", "0", "X", "-"}:
                continue
            numero = str(valor).strip()
            if len(numero) > 10 or numero in vistos:
                raise ValueError("Hay números de asiento duplicados o inválidos.")
            vistos.add(numero)
            nuevos.append(Asiento(numero_asiento=numero, fila=fila_idx, columna=col_idx))
    if len(nuevos) != plantilla.cantidad_asientos or len(nuevos) != v.cantidad_asientos:
        raise ValueError("La matriz no coincide con la cantidad de asientos declarada.")
    v.asientos.extend(nuevos)


@vehiculos_bp.get("/")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def listar():
    q = Vehiculo.query
    if not es_admin():
        q = q.filter_by(id_propietario=current_user.id_usuario)
    if request.args.get("incluir_inactivos") != "1":
        q = q.filter(Vehiculo.activo.is_(True))
    return jsonify(ok=True, datos=[serializar(v) for v in q.order_by(Vehiculo.id_vehiculo.desc()).all()])


@vehiculos_bp.get("/<int:id_vehiculo>")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def obtener(id_vehiculo):
    v = db.session.get(Vehiculo, id_vehiculo)
    if not v:
        return error("Vehículo no encontrado.", 404)
    if not puede_operar(v):
        return error("No puede consultar un vehículo de otro propietario.", 403)
    return jsonify(ok=True, dato=serializar(v))


@vehiculos_bp.post("/")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def crear():
    p = request.get_json(silent=True) or request.form
    try:
        id_prop = int(p.get("id_propietario")) if es_admin() else current_user.id_usuario
        id_plantilla = int(p.get("id_plantilla"))
        cantidad = int(p.get("cantidad_asientos"))
    except (TypeError, ValueError):
        return error("Propietario, plantilla y cantidad de asientos son obligatorios.")
    usuario = db.session.get(Usuario, id_prop)
    perfil = Propietario.query.filter_by(id_usuario=id_prop, activo=True).first()
    plantilla = db.session.get(PlantillaAsientos, id_plantilla)
    if not usuario or usuario.rol != "PROPIETARIO" or not usuario.activo or not perfil:
        return error("El usuario no tiene un perfil de propietario activo.", 422)
    if not plantilla or not plantilla.activo:
        return error("La plantilla no existe o está inactiva.", 422)
    if cantidad != plantilla.cantidad_asientos:
        return error("La cantidad de asientos no coincide con la plantilla.", 422)
    placa = str(p.get("placa", "")).strip().upper()
    marca = str(p.get("marca") or "").strip() or None
    modelo = str(p.get("modelo", "")).strip()
    tipo = str(p.get("tipo", "")).strip().upper()
    if not placa or len(placa) > 20 or not modelo or len(modelo) > 100 or tipo not in TIPOS:
        return error("Placa, modelo o tipo de vehículo inválidos.")
    v = Vehiculo(id_propietario=id_prop, id_plantilla=id_plantilla, placa=placa,
                 marca=marca, modelo=modelo, tipo=tipo, cantidad_asientos=cantidad)
    db.session.add(v)
    try:
        db.session.flush()
        generar_asientos(v, plantilla)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("La placa ya está registrada.", 409)
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc), 422)
    return jsonify(ok=True, mensaje="Vehículo registrado.", dato=serializar(v)), 201


@vehiculos_bp.put("/<int:id_vehiculo>")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def editar(id_vehiculo):
    v = db.session.get(Vehiculo, id_vehiculo)
    if not v:
        return error("Vehículo no encontrado.", 404)
    if not puede_operar(v):
        return error("No puede modificar un vehículo de otro propietario.", 403)
    p = request.get_json(silent=True) or request.form
    placa = str(p.get("placa", v.placa)).strip().upper()
    marca = str(p.get("marca", v.marca or "")).strip() or None
    modelo = str(p.get("modelo", v.modelo)).strip()
    tipo = str(p.get("tipo", v.tipo)).strip().upper()
    if not placa or len(placa) > 20 or not modelo or len(modelo) > 100 or tipo not in TIPOS:
        return error("Datos del vehículo inválidos.")
    if es_admin() and p.get("id_propietario") is not None:
        try:
            nuevo_id = int(p["id_propietario"])
        except (ValueError, TypeError):
            return error("Propietario inválido.")
        nuevo = db.session.get(Usuario, nuevo_id)
        perfil = Propietario.query.filter_by(id_usuario=nuevo_id, activo=True).first()
        if not nuevo or nuevo.rol != "PROPIETARIO" or not nuevo.activo or not perfil:
            return error("El nuevo propietario no tiene perfil activo.", 422)
        v.id_propietario = nuevo_id
    if p.get("id_plantilla") is not None:
        try:
            id_plantilla = int(p["id_plantilla"])
        except (ValueError, TypeError):
            return error("Plantilla inválida.")
        plantilla = db.session.get(PlantillaAsientos, id_plantilla)
        if not plantilla or not plantilla.activo or plantilla.cantidad_asientos != v.cantidad_asientos:
            return error("Plantilla inexistente, inactiva o incompatible.", 422)
        if id_plantilla != v.id_plantilla:
            try:
                generar_asientos(v, plantilla, reemplazar=True)
            except ValueError as exc:
                db.session.rollback()
                return error(str(exc), 409)
            v.id_plantilla = id_plantilla
    v.placa, v.marca, v.modelo, v.tipo = placa, marca, modelo, tipo
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("No se pudo guardar: la placa podría estar duplicada.", 409)
    return jsonify(ok=True, mensaje="Vehículo actualizado.", dato=serializar(v))


@vehiculos_bp.post("/<int:id_vehiculo>/generar-asientos")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def regenerar(id_vehiculo):
    v = db.session.get(Vehiculo, id_vehiculo)
    if not v:
        return error("Vehículo no encontrado.", 404)
    if not puede_operar(v):
        return error("No puede operar este vehículo.", 403)
    try:
        generar_asientos(v, v.plantilla, reemplazar=True)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc), 409)
    return jsonify(ok=True, cantidad=len(v.asientos))


@vehiculos_bp.patch("/<int:id_vehiculo>/estado")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def cambiar_estado(id_vehiculo):
    v = db.session.get(Vehiculo, id_vehiculo)
    if not v:
        return error("Vehículo no encontrado.", 404)
    if not puede_operar(v):
        return error("No puede operar este vehículo.", 403)
    p = request.get_json(silent=True) or {}
    if not isinstance(p.get("activo"), bool):
        return error("El campo activo debe ser booleano.")
    if not p["activo"] and any(x.estado in {"PROGRAMADO", "ACTIVO", "EN_CURSO"} for x in v.viajes):
        return error("No se desactiva: el vehículo tiene viajes vigentes.", 409)
    v.activo = p["activo"]
    db.session.commit()
    return jsonify(ok=True, activo=v.activo)


@vehiculos_bp.delete("/<int:id_vehiculo>")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def eliminar(id_vehiculo):
    v = db.session.get(Vehiculo, id_vehiculo)
    if not v:
        return error("Vehículo no encontrado.", 404)
    if not puede_operar(v):
        return error("No puede eliminar un vehículo de otro propietario.", 403)
    if v.viajes or any(a.reservas for a in v.asientos):
        return error("Tiene viajes o reservas asociados. Desactívelo en lugar de eliminarlo.", 409)
    db.session.delete(v)
    db.session.commit()
    return jsonify(ok=True, mensaje="Vehículo eliminado.")
