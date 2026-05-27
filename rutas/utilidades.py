"""
rutas/utilidades.py
Decoradores y funciones auxiliares usadas en todas las rutas.
"""
from functools import wraps
from flask import session, redirect, url_for, flash
import modelos.usuario as Usuario

def usuario_actual():
    """Retorna el usuario en sesion o None si no hay sesion activa."""
    if 'usuario_id' not in session:
        return None
    return Usuario.buscar_por_id(session['usuario_id'])

def cantidad_carrito():
    """Suma el total de items en el carrito para el badge del navbar."""
    carrito = session.get('carrito', {})
    return sum(carrito.values())

def requiere_login(f):
    """Decorador: redirige al login si el usuario no tiene sesion activa."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion primero.', 'warning')
            return redirect(url_for('autenticacion.login'))
        return f(*args, **kwargs)
    return wrapper

def requiere_admin(f):
    """Decorador: solo permite acceso a usuarios con rol admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion primero.', 'warning')
            return redirect(url_for('autenticacion.login'))
        # Si el usuario no es admin, redirige a la tienda
        if session.get('usuario_rol') != 'admin':
            flash('No tienes permisos para esa seccion.', 'danger')
            return redirect(url_for('tienda.index'))
        return f(*args, **kwargs)
    return wrapper
