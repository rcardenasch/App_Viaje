from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from modelos import db
from modelos.viaje import Viaje
from modelos.asiento import Asiento
from modelos.reserva import Reserva
from modelos.bloqueo_asiento import BloqueoAsiento
from rutas._comun import error, roles_requeridos

reservas_bp = Blueprint("reservas", __name__)
MINUTOS_BLOQUEO = 5


def _utc(dt):
    # PostgreSQL puede devolver datetime sin tzinfo según el tipo/driver.
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _liberar_vencidos(id_viaje=None):
    ahora = datetime.now(timezone.utc)
    q = BloqueoAsiento.query.filter(BloqueoAsiento.estado == "ACTIVO")
    if id_viaje is not None:
        q = q.filter_by(id_viaje=id_viaje)
    for b in q.all():
        if _utc(b.fecha_expiracion) <= ahora:
            b.estado = "VENCIDO"


def _obtener_viaje_bloqueado(id_viaje):
    v = db.session.execute(select(Viaje).where(
        Viaje.id_viaje == id_viaje).with_for_update()).scalar_one_or_none()
    if not v:
        return None, error("Viaje no encontrado.", 404)
    if v.estado not in {"PROGRAMADO", "ACTIVO"}:
        return None, error("El viaje no admite reservas.", 409)
    if v.fecha_salida < datetime.now().date():
        return None, error("La fecha del viaje ya pasó.", 409)
    return v, None


@reservas_bp.get("/reserva")
@login_required
def pagina_reserva():
    return render_template("reserva.html")


@reservas_bp.get("/api/viajes/<int:id_viaje>/asientos")
def consultar_asientos(id_viaje):
    v = db.session.get(Viaje, id_viaje)
    if not v:
        return error("Viaje no encontrado.", 404)
    _liberar_vencidos(id_viaje)
    db.session.commit()
    ahora = datetime.now(timezone.utc)
    confirmados = {r.id_asiento for r in v.reservas if r.estado == "CONFIRMADA"}
    bloqueados = {b.id_asiento for b in v.bloqueos if b.estado == "ACTIVO"
                  and _utc(b.fecha_expiracion) > ahora}
    salida = []
    for a in sorted(v.vehiculo.asientos, key=lambda x: (x.fila, x.columna)):
        estado = "OCUPADO" if a.id_asiento in confirmados else (
            "BLOQUEADO" if a.id_asiento in bloqueados else "DISPONIBLE")
        salida.append({"id_asiento": a.id_asiento, "numero_asiento": a.numero_asiento,
                       "fila": a.fila, "columna": a.columna, "estado": estado})
    return jsonify(ok=True, id_viaje=id_viaje, asientos=salida)


@reservas_bp.post("/api/reservas/bloquear")
@login_required
@roles_requeridos("PASAJERO", "ADMINISTRADOR")
def bloquear_asiento():
    p = request.get_json(silent=True) or {}
    try:
        id_viaje, id_asiento = int(p.get("id_viaje")), int(p.get("id_asiento"))
    except (TypeError, ValueError):
        return error("Debe indicar un viaje y un asiento válidos.")
    v, respuesta = _obtener_viaje_bloqueado(id_viaje)
    if respuesta:
        return respuesta
    # Serializar por viaje y asiento para reducir carreras concurrentes.
    asiento = db.session.execute(select(Asiento).where(
        Asiento.id_asiento == id_asiento,
        Asiento.id_vehiculo == v.id_vehiculo).with_for_update()).scalar_one_or_none()
    if not asiento:
        db.session.rollback()
        return error("El asiento no pertenece al vehículo de este viaje.", 422)
    _liberar_vencidos(id_viaje)
    confirmado = Reserva.query.filter_by(id_viaje=id_viaje, id_asiento=id_asiento,
                                         estado="CONFIRMADA").first()
    activo = BloqueoAsiento.query.filter_by(id_viaje=id_viaje, id_asiento=id_asiento,
                                           estado="ACTIVO").first()
    if confirmado or activo:
        db.session.rollback()
        return error("El asiento ya no está disponible.", 409)
    bloqueo = BloqueoAsiento(
        id_viaje=id_viaje, id_asiento=id_asiento,
        id_usuario=current_user.id_usuario,
        fecha_expiracion=datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_BLOQUEO)
    )
    db.session.add(bloqueo)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Otro pasajero acaba de bloquear este asiento. Actualice el mapa.", 409)
    return jsonify(ok=True, token=bloqueo.token,
                   vence=_utc(bloqueo.fecha_expiracion).isoformat(),
                   minutos=MINUTOS_BLOQUEO), 201


@reservas_bp.post("/api/reservas/confirmar")
@login_required
@roles_requeridos("PASAJERO", "ADMINISTRADOR")
def confirmar_reserva():
    p = request.get_json(silent=True) or {}
    token = str(p.get("token", "")).strip()
    if not token:
        return error("El token de bloqueo es obligatorio.")
    bloqueo = db.session.execute(select(BloqueoAsiento).where(
        BloqueoAsiento.token == token).with_for_update()).scalar_one_or_none()
    if not bloqueo:
        return error("Bloqueo no encontrado.", 404)
    if bloqueo.id_usuario != current_user.id_usuario and current_user.rol != "ADMINISTRADOR":
        return error("Este bloqueo pertenece a otro usuario.", 403)
    ahora = datetime.now(timezone.utc)
    if bloqueo.estado != "ACTIVO" or _utc(bloqueo.fecha_expiracion) <= ahora:
        bloqueo.estado = "VENCIDO"
        db.session.commit()
        return error("El bloqueo venció. Seleccione nuevamente el asiento.", 409)
    v, respuesta = _obtener_viaje_bloqueado(bloqueo.id_viaje)
    if respuesta:
        return respuesta
    clave = str(p.get("clave_idempotencia") or "").strip() or None
    if clave:
        anterior = Reserva.query.filter_by(clave_idempotencia=clave).first()
        if anterior:
            if anterior.id_pasajero != current_user.id_usuario:
                return error("La clave de idempotencia ya fue utilizada.", 409)
            return jsonify(ok=True, codigo_reserva=anterior.codigo_reserva,
                           estado=anterior.estado, repetida=True)
    existente = Reserva.query.filter_by(id_viaje=v.id_viaje,
                                        id_asiento=bloqueo.id_asiento,
                                        estado="CONFIRMADA").first()
    if existente:
        return error("El asiento ya tiene una reserva confirmada.", 409)
    reserva = Reserva(id_viaje=v.id_viaje, id_asiento=bloqueo.id_asiento,
                      id_pasajero=current_user.id_usuario, importe=v.precio,
                      estado="CONFIRMADA", fecha_confirmacion=ahora,
                      clave_idempotencia=clave)
    bloqueo.estado = "CONSUMIDO"
    db.session.add(reserva)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("El asiento fue reservado por otra solicitud. Actualice la disponibilidad.", 409)
    return jsonify(ok=True, mensaje="Reserva confirmada.",
                   codigo_reserva=reserva.codigo_reserva,
                   estado=reserva.estado, importe=str(reserva.importe)), 201


@reservas_bp.get("/api/mis-reservas")
@login_required
def mis_reservas():
    reservas = Reserva.query.filter_by(id_pasajero=current_user.id_usuario).order_by(
        Reserva.fecha_reserva.desc()).all()
    datos = [{"codigo_reserva": r.codigo_reserva, "estado": r.estado,
              "importe": str(r.importe), "id_viaje": r.id_viaje,
              "origen": r.viaje.origen, "destino": r.viaje.destino,
              "fecha_salida": r.viaje.fecha_salida.isoformat(),
              "hora_salida": r.viaje.hora_salida.strftime("%H:%M"),
              "asiento": r.asiento.numero_asiento} for r in reservas]
    return jsonify(ok=True, datos=datos)


@reservas_bp.post("/api/reservas/<string:codigo>/cancelar")
@login_required
def cancelar_reserva(codigo):
    r = Reserva.query.filter_by(codigo_reserva=codigo).with_for_update().first()
    if not r:
        return error("Reserva no encontrada.", 404)
    if r.id_pasajero != current_user.id_usuario and current_user.rol != "ADMINISTRADOR":
        return error("No puede cancelar una reserva de otro pasajero.", 403)
    if r.estado != "CONFIRMADA":
        return error("Solo se pueden cancelar reservas confirmadas.", 409)
    if r.viaje.fecha_salida <= datetime.now().date():
        return error("No se puede cancelar el día de salida o después.", 409)
    r.estado = "CANCELADA"
    db.session.commit()
    return jsonify(ok=True, mensaje="Reserva cancelada.")
