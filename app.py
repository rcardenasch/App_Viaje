
from flask import Flask, render_template

from configuracion import Configuracion
from modelos import db
from flask_migrate import Migrate


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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5088,
        debug=True
    )
