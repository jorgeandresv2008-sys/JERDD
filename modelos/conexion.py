"""
modelos/conexion.py
Maneja la conexion a la base de datos SQLite.
"""
import sqlite3
import os

def get_db():
    """
    Abre una conexion a la base de datos SQLite.
    row_factory permite acceder a las columnas por nombre en lugar de indice.
    """
    os.makedirs('base_datos', exist_ok=True)
    conn = sqlite3.connect('base_datos/jerdd.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar_bd():
    """
    Crea las tablas si no existen leyendo el archivo schema.sql.
    Se llama una sola vez al arrancar la aplicacion.
    """
    conn = get_db()
    with open('base_datos/schema.sql', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
