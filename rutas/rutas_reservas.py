from flask import Flask, render_template
from flask_login import login_required

reservas_bp = Flask(__name__)

reservas_bp.get("/reserva")

@login_required
def pagina_reserva():
    return render_template("reserva.html")