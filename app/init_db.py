
import os
import psycopg

from dotenv import load_dotenv

load_dotenv()


def conectar():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(
            database_url,
            connect_timeout=10
        )

    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=10
    )


def inicializar_base_datos():

    usuarios = [
        (
            os.environ["DEMO_USER1"],
            os.environ["DEMO_PASSWORD1"],
            os.environ["DEMO_NAME1"]
        ),
        (
            os.environ["DEMO_USER2"],
            os.environ["DEMO_PASSWORD2"],
            os.environ["DEMO_NAME2"]
        )
    ]

    with conectar() as conexion:
        with conexion.cursor() as cursor:

            cursor.execute(
                "CREATE EXTENSION IF NOT EXISTS pgcrypto"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id BIGSERIAL PRIMARY KEY,
                    usuario VARCHAR(60) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre VARCHAR(120) NOT NULL
                )
            """)

            for usuario, password, nombre in usuarios:

                cursor.execute("""
                    INSERT INTO usuarios
                        (usuario, password_hash, nombre)
                    VALUES (
                        %s,
                        crypt(%s, gen_salt('bf', 12)),
                        %s
                    )
                    ON CONFLICT (usuario) DO NOTHING
                """, (usuario, password, nombre))

    print("Base de datos inicializada correctamente")


if __name__ == "__main__":
    inicializar_base_datos()
