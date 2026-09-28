import os
import secrets

from flask import Flask, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from math import ceil
from threading import Lock
from time import monotonic

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
csrf = CSRFProtect(app)

# Usuario de ejemplo para practicar, sin base de datos.
USUARIO = "admin"
PASSWORD_HASH = generate_password_hash("123456")

MAX_INTENTOS = 3
SEGUNDOS_BLOQUEO = 30

intentos_login = {}
lock_login = Lock()





@app.route("/", methods=["GET"])
def inicio():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("inicio.html", usuario=session["usuario"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("inicio"))

    error = None
    
    if request.method == "POST":
        ip = request.remote_addr
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        confirmar_password = request.form.get("confirmar_password", "")

        with lock_login:
            ahora = monotonic()
            estado = intentos_login.setdefault(
                ip, 
                {"fallos": 0, "bloqueado_hasta": 0}
            )

            if estado["bloqueado_hasta"] > ahora:
                segundos = ceil(estado["bloqueado_hasta"] - ahora)
                error = f"Has excedido el numero de intentos. Intenta nuevamente en {segundos} segundos."
                return (
                    render_template("login.html", error=error),
                    429,
                    {"Retry-After": str(segundos)}
                )

            #Si termino el bloqueo permite tres nuevos intentos
            if estado["bloqueado_hasta"] != 0:
                estado["fallos"] = 0
                estado["bloqueado_hasta"] = 0

            if not password or any(caracter not in "0123456789" for caracter in password):
                error = "La contraseña debe contener solo números del 0 al 9."
                return render_template("login.html", error=error), 400

            if password != confirmar_password:
                error = "Las contraseñas no coinciden."
                return render_template("login.html", error=error), 400
            
            if password != confirmar_password:
                error = "Las contraseñas no coinciden."
                return render_template("login.html", error=error), 400

            

            password_valido = check_password_hash(PASSWORD_HASH, password)

            if usuario == USUARIO and password_valido:
                    intentos_login.pop(ip, None)
                    session.clear()
                    session["usuario"] = usuario
                    return redirect(url_for("inicio"))

            estado["fallos"] += 1
                    
            if estado["fallos"] >= MAX_INTENTOS:
                        estado["bloqueado_hasta"] = (
                            monotonic() + SEGUNDOS_BLOQUEO
                        )
                        error = (
                            "Has excedido el numero de intentos. "
                            "Intenta nuevamente en 30 segundos."
                        )

                        return (
                            render_template("login.html", error=error),
                            429,
                            {"Retry-After": str(SEGUNDOS_BLOQUEO)}
                        )

            restantes = MAX_INTENTOS - estado["fallos"]
            error = (
                            "Usuario o contraseña incorrectos."
                            f"Intentos restantes: {restantes}"
                )

    return render_template("login.html", error=error)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()

# from flask import Flask, jsonify
# import requests

# from services.clima_service import obtener_clima

# app = Flask(__name__)


# @app.get("/api/clima")
# def consultar_clima():
#     try:
#         clima = obtener_clima()
#         return jsonify(clima), 200

#     except requests.exceptions.Timeout:
#         return jsonify({
#             "error": "El servicio del clima tardó demasiado."
#         }), 504

#     except requests.exceptions.RequestException:
#         return jsonify({
#             "error": "No se pudo consultar el servicio del clima."
#         }), 502


# if __name__ == "__main__":
#     app.run(debug=True)