
from flask import Flask, render_template

from configuracion import Configuracion
from modelos import db
from flask_migrate import Migrate

from rutas.rutas_reservas import reservas_bp
from rutas.rutas_viajes import viajes_bp
from rutas.rutas_ubicaciones import ubicaciones_bp
from rutas.rutas_vehiculos import vehiculos_bp



def crear_aplicacion():

    app = Flask(__name__)

    app.config.from_object(Configuracion)

    db.init_app(app)

    Migrate(app, db)

    @app.get("/")
    def inicio():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"estado": "ok"}

    return app


app = crear_aplicacion()


app.register_blueprint(reservas_bp)
app.register_blueprint(viajes_bp)
app.register_blueprint(ubicaciones_bp) 
app.register_blueprint(vehiculos_bp)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5088,
        debug=True
    )
