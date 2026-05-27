"""
rutas/autenticacion.py
Rutas de login, registro y logout.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import modelos.usuario as Usuario

# Blueprint agrupa las rutas de autenticacion
autenticacion = Blueprint('autenticacion', __name__)

@autenticacion.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email     = request.form['email'].strip().lower()
        contrasena = request.form['contrasena']

        # Busca el usuario en la BD por email
        usuario = Usuario.buscar_por_email(email)

        # Verifica la contrasena con bcrypt
        if usuario and Usuario.verificar_contrasena(usuario['contrasena_hash'], contrasena):
            session['usuario_id']     = usuario['id']
            session['usuario_rol']    = usuario['rol']
            session['usuario_nombre'] = usuario['nombre']
            flash(f'Bienvenido, {usuario["nombre"]}!', 'success')

            # Redirige segun el rol del usuario
            if usuario['rol'] == 'admin':
                return redirect(url_for('administrador.dashboard'))
            return redirect(url_for('tienda.index'))
        else:
            flash('Email o contrasena incorrectos.', 'danger')

    return render_template('login.html')

@autenticacion.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre     = request.form['nombre'].strip()
        email      = request.form['email'].strip().lower()
        contrasena  = request.form['contrasena']
        contrasena2 = request.form['contrasena2']

        # Validaciones antes de crear la cuenta
        if not nombre or len(nombre) < 2:
            flash('El nombre debe tener al menos 2 caracteres.', 'danger')
            return render_template('registro.html')
        if len(contrasena) < 6:
            flash('La contrasena debe tener al menos 6 caracteres.', 'danger')
            return render_template('registro.html')
        if contrasena != contrasena2:
            flash('Las contrasenas no coinciden.', 'danger')
            return render_template('registro.html')

        try:
            Usuario.crear_usuario(nombre, email, contrasena)
            flash('Cuenta creada. Ya puedes iniciar sesion.', 'success')
            return redirect(url_for('autenticacion.login'))
        except Exception:
            flash('Ya existe una cuenta con ese email.', 'danger')

    return render_template('registro.html')

@autenticacion.route('/logout')
def logout():
    session.clear()
    flash('Sesion cerrada.', 'info')
    return redirect(url_for('autenticacion.login'))
