
import os


class Configuracion:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "cambiar-esta-clave-en-produccion"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:123456@localhost:5433/App_Viaje"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800
    }

    JSON_SORT_KEYS = False
