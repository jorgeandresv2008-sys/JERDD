"""
app.py - Punto de entrada de JERDD
Configura Flask y registra los blueprints (modulos de rutas).
Toda la logica esta distribuida en las carpetas rutas/ y modelos/.
"""
import os
from flask import Flask, redirect, url_for
from modelos.conexion import inicializar_bd

# ── Configuracion de Flask ──────────────────────────────
app = Flask(__name__,
            template_folder='plantillas',   # carpeta de plantillas HTML
            static_folder='estatico')       # carpeta de archivos estaticos

app.secret_key = 'jerdd_clave_secreta_2024'

# ── Registro de blueprints (modulos de rutas) ───────────
# Cada blueprint maneja un grupo de URLs relacionadas
from rutas.autenticacion import autenticacion
from rutas.tienda        import tienda
from rutas.administrador import administrador

app.register_blueprint(autenticacion)
app.register_blueprint(tienda)
app.register_blueprint(administrador)

# ── Ruta raiz ───────────────────────────────────────────
@app.route('/')
def index():
    """La raiz redirige al login."""
    return redirect(url_for('autenticacion.login'))

# ── Arranque ────────────────────────────────────────────
if __name__ == '__main__':
    # Crea las tablas al arrancar si no existen
    inicializar_bd()
    print("JERDD corriendo en http://localhost:5000")
    print("Admin:   admin@jerdd.com  / admin123")
    print("Cliente: juan@test.com    / cliente123")
    app.run(debug=True, port=5000)
