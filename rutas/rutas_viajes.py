from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_login import current_user
from modelos import db
from modelos.viaje import Viaje
from modelos.vehiculo import Vehiculo
from modelos.ubicacion import Ubicacion
from modelos.reserva import Reserva
from modelos.bloqueo_asiento import BloqueoAsiento
from rutas._comun import error, roles_requeridos, es_admin

viajes_bp = Blueprint("viajes", __name__, url_prefix="/viajes")
ESTADOS_GESTIONABLES = {"PROGRAMADO", "ACTIVO"}


def _disponibilidad(v):
    ahora = datetime.now(timezone.utc)
    confirmados = {r.id_asiento for r in v.reservas if r.estado == "CONFIRMADA"}
    bloqueados = {b.id_asiento for b in v.bloqueos
                  if b.estado == "ACTIVO" and b.fecha_expiracion > ahora}
    ocupados = confirmados | bloqueados
    total = len(v.vehiculo.asientos)
    return {"total": total, "ocupados": len(ocupados),
            "disponibles": max(0, total - len(ocupados))}


def serializar(v):
    return {"id_viaje": v.id_viaje, "id_vehiculo": v.id_vehiculo,
            "origen": v.origen, "destino": v.destino,
            "id_origen": v.id_origen, "id_destino": v.id_destino,
            "ubicacion_origen": v.ubicacion_origen.nombre_completo if v.ubicacion_origen else None,
            "ubicacion_destino": v.ubicacion_destino.nombre_completo if v.ubicacion_destino else None,
            "fecha_salida": v.fecha_salida.isoformat(),
            "hora_salida": v.hora_salida.strftime("%H:%M"),
            "hora_llegada": v.hora_llegada.strftime("%H:%M") if v.hora_llegada else None,
            "precio": str(v.precio), "estado": v.estado,
            "disponibilidad": _disponibilidad(v)}


def validar_datos(p, actual=None):
    try:
        id_vehiculo = int(p.get("id_vehiculo", actual.id_vehiculo if actual else 0))
        fecha_txt = p.get("fecha_salida", actual.fecha_salida.isoformat() if actual else "")
        hora_txt = p.get("hora_salida", actual.hora_salida.strftime("%H:%M") if actual else "")
        fecha = date.fromisoformat(str(fecha_txt))
        hora = time.fromisoformat(str(hora_txt))
        precio = Decimal(str(p.get("precio", actual.precio if actual else "")))
    except (ValueError, TypeError, InvalidOperation):
        return None, "Vehículo, fecha, hora o precio tienen un formato inválido."
    if not precio.is_finite() or precio < 0 or precio > Decimal("99999999.99"):
        return None, "El precio debe ser un importe válido mayor o igual a cero."
    vehiculo = db.session.get(Vehiculo, id_vehiculo)
    if not vehiculo or not vehiculo.activo:
        return None, "El vehículo no existe o está inactivo."
    if not es_admin() and vehiculo.id_propietario != current_user.id_usuario:
        return None, "No puede programar viajes con vehículos de otro propietario."
    if fecha < date.today():
        return None, "La fecha de salida no puede estar en el pasado."
    if fecha == date.today() and hora <= datetime.now().time().replace(tzinfo=None):
        return None, "La hora de salida ya pasó."

    id_origen = p.get("id_origen", actual.id_origen if actual else None)
    id_destino = p.get("id_destino", actual.id_destino if actual else None)
    origen = str(p.get("origen", actual.origen if actual else "")).strip()
    destino = str(p.get("destino", actual.destino if actual else "")).strip()
    u_origen = u_destino = None
    try:
        if id_origen not in (None, ""):
            u_origen = db.session.get(Ubicacion, int(id_origen))
        if id_destino not in (None, ""):
            u_destino = db.session.get(Ubicacion, int(id_destino))
    except (ValueError, TypeError):
        return None, "Los identificadores de ubicación deben ser números válidos."
    if id_origen not in (None, "") and (not u_origen or not u_origen.activo):
        return None, "La ubicación de origen no existe o está inactiva."
    if id_destino not in (None, "") and (not u_destino or not u_destino.activo):
        return None, "La ubicación de destino no existe o está inactiva."
    if u_origen:
        origen = u_origen.nombre
    if u_destino:
        destino = u_destino.nombre
    if not origen or not destino or origen.casefold() == destino.casefold():
        return None, "Origen y destino son obligatorios y deben ser distintos."
    if len(origen) > 150 or len(destino) > 150:
        return None, "Origen y destino no pueden superar 150 caracteres."
    llegada_txt = p.get("hora_llegada", actual.hora_llegada.strftime("%H:%M") if actual and actual.hora_llegada else None)
    try:
        llegada = time.fromisoformat(str(llegada_txt)) if llegada_txt else None
    except ValueError:
        return None, "La hora de llegada no tiene un formato válido."
    if llegada and llegada <= hora:
        return None, "La hora de llegada debe ser posterior a la hora de salida."
    return {"id_vehiculo": id_vehiculo, "id_origen": int(id_origen) if id_origen not in (None, "") else None,
            "id_destino": int(id_destino) if id_destino not in (None, "") else None,
            "origen": origen, "destino": destino, "fecha_salida": fecha,
            "hora_salida": hora, "hora_llegada": llegada, "precio": precio}, None


@viajes_bp.get("/")
def buscar():
    q = Viaje.query.join(Vehiculo).filter(Viaje.estado.in_(("PROGRAMADO", "ACTIVO")),
                                          Vehiculo.activo.is_(True))
    origen = request.args.get("origen", "").strip()
    destino = request.args.get("destino", "").strip()
    fecha_txt = request.args.get("fecha", "").strip()
    if origen:
        q = q.filter(Viaje.origen.ilike(f"%{origen}%"))
    if destino:
        q = q.filter(Viaje.destino.ilike(f"%{destino}%"))
    if fecha_txt:
        try:
            q = q.filter(Viaje.fecha_salida == date.fromisoformat(fecha_txt))
        except ValueError:
            return error("La fecha de búsqueda debe tener formato AAAA-MM-DD.")
    viajes = q.order_by(Viaje.fecha_salida, Viaje.hora_salida).all()
    return jsonify(ok=True, datos=[serializar(v) for v in viajes])


@viajes_bp.get("/<int:id_viaje>")
def detalle(id_viaje):
    v = db.session.get(Viaje, id_viaje)
    if not v:
        return error("Viaje no encontrado.", 404)
    return jsonify(ok=True, dato=serializar(v))


@viajes_bp.post("/")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def crear():
    p, mensaje = validar_datos(request.get_json(silent=True) or request.form)
    if mensaje:
        return error(mensaje, 422)
    v = Viaje(**p)
    db.session.add(v)
    db.session.commit()
    return jsonify(ok=True, mensaje="Viaje registrado.", dato=serializar(v)), 201


@viajes_bp.put("/<int:id_viaje>")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def editar(id_viaje):
    v = db.session.get(Viaje, id_viaje)
    if not v:
        return error("Viaje no encontrado.", 404)
    if not es_admin() and v.vehiculo.id_propietario != current_user.id_usuario:
        return error("No puede modificar este viaje.", 403)
    if v.estado not in ESTADOS_GESTIONABLES:
        return error("Solo se pueden editar viajes programados o activos.", 409)
    if any(r.estado == "CONFIRMADA" for r in v.reservas):
        return error("No se modifica un viaje que ya tiene reservas confirmadas.", 409)
    p, mensaje = validar_datos(request.get_json(silent=True) or request.form, v)
    if mensaje:
        return error(mensaje, 422)
    for campo, valor in p.items():
        setattr(v, campo, valor)
    db.session.commit()
    return jsonify(ok=True, mensaje="Viaje actualizado.", dato=serializar(v))


@viajes_bp.post("/<int:id_viaje>/cancelar")
@roles_requeridos("ADMINISTRADOR", "PROPIETARIO")
def cancelar(id_viaje):
    v = db.session.get(Viaje, id_viaje)
    if not v:
        return error("Viaje no encontrado.", 404)
    if not es_admin() and v.vehiculo.id_propietario != current_user.id_usuario:
        return error("No puede cancelar este viaje.", 403)
    if v.estado in {"CANCELADO", "FINALIZADO"}:
        return error("El viaje ya está cerrado.", 409)
    v.estado = "CANCELADO"
    for bloqueo in v.bloqueos:
        if bloqueo.estado == "ACTIVO":
            bloqueo.estado = "LIBERADO"
    for reserva in v.reservas:
        if reserva.estado in {"PENDIENTE", "CONFIRMADA"}:
            reserva.estado = "CANCELADA"
    db.session.commit()
    return jsonify(ok=True, mensaje="Viaje cancelado; reservas y bloqueos liberados.")


@viajes_bp.get("/<int:id_viaje>/disponibilidad")
def consultar_disponibilidad(id_viaje):
    v = db.session.get(Viaje, id_viaje)
    if not v:
        return error("Viaje no encontrado.", 404)
    return jsonify(ok=True, **_disponibilidad(v))
