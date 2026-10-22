
import os
import psycopg

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session
)
from dotenv import load_dotenv


# ==========================================
# 1. CONFIGURACION INICIAL
# ==========================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ==========================================
# 2. CONEXION A POSTGRESQL
# ==========================================


def obtener_conexion():

    # Conexión administrada de Blitz Cloud
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(
            database_url,
            connect_timeout=10
        )

    # Conexión local mediante Docker Compose
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5
    )



# ==========================================
# 3. PAGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    if "usuario_id" in session:
        return redirect(url_for("bienvenida"))

    return redirect(url_for("mostrar_login"))


# ==========================================
# 4. INICIO DE SESION
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def mostrar_login():

    if "usuario_id" in session:
        return redirect(url_for("bienvenida"))

    if request.method == "POST":

        usuario = request.form.get(
            "usuario", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        # Validar campos vacios
        if not usuario or not password:
            return render_template(
                "login.html",
                error="Por favor, completa todos los campos."
            ), 400

        # Consultar credenciales en PostgreSQL
        try:
            with obtener_conexion() as conexion:

                with conexion.cursor() as cursor:

                    consulta = """
                        SELECT id, nombre
                        FROM usuarios
                        WHERE usuario = %s
                        AND password_hash = crypt(
                            %s,
                            password_hash
                        )
                    """

                    cursor.execute(
                        consulta,
                        (usuario, password)
                    )

                    resultado = cursor.fetchone()

        except psycopg.Error:
            app.logger.exception(
                "Error de conexion o consulta PostgreSQL"
            )

            return render_template(
                "login.html",
                error="El servicio no esta disponible. Intenta nuevamente."
            ), 503

        # Credenciales incorrectas
        if resultado is None:
            return render_template(
                "login.html",
                error="Usuario o contraseña incorrectos."
            ), 401

        # Credenciales correctas
        usuario_id, nombre = resultado

        session.clear()

        session["usuario_id"] = usuario_id
        session["nombre"] = nombre

        return redirect(url_for("bienvenida"))

    return render_template("login.html")


# ==========================================
# 5. PAGINA DE BIENVENIDA PROTEGIDA
# ==========================================

@app.route("/bienvenida")
def bienvenida():

    # Verificar si existe una sesion
    if "usuario_id" not in session:
        return redirect(url_for("mostrar_login"))

    nombre = session.get("nombre", "Usuario")

    return render_template(
        "bienvenida.html",
        nombre=nombre
    )


# ==========================================
# 6. CERRAR SESION
# ==========================================

@app.route("/salir")
def salir():

    # Eliminar la sesion actual
    session.clear()

    return redirect(url_for("mostrar_login"))
