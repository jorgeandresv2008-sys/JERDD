"""
modelos/usuario.py
Funciones de base de datos relacionadas con usuarios:
registro, login, perfil, listado para admin.
"""
import bcrypt
from modelos.conexion import get_db

def buscar_por_email(email):
    """Busca un usuario por email para el proceso de login."""
    conn = get_db()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return usuario

def buscar_por_id(user_id):
    """Obtiene un usuario por su id. Flask lo llama en cada peticion autenticada."""
    conn = get_db()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return usuario

def crear_usuario(nombre, email, contrasena):
    """
    Crea un nuevo cliente. Convierte la contrasena a hash con bcrypt
    antes de guardarla, nunca se guarda la contrasena en texto plano.
    """
    # bcrypt.gensalt() genera un salt aleatorio que se incluye en el hash
    contrasena_hash = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()
    conn = get_db()
    conn.execute(
        "INSERT INTO usuarios (nombre, email, contrasena_hash, rol) VALUES (?, ?, ?, 'cliente')",
        (nombre, email, contrasena_hash)
    )
    conn.commit()
    conn.close()

def verificar_contrasena(hash_guardado, contrasena_ingresada):
    """
    Verifica la contrasena comparando el hash guardado con la ingresada.
    bcrypt.checkpw recalcula el hash usando el salt embebido y compara.
    """
    return bcrypt.checkpw(contrasena_ingresada.encode(), hash_guardado.encode())

def actualizar_datos(user_id, nombre, telefono, direccion):
    """Actualiza los datos personales del usuario."""
    conn = get_db()
    conn.execute(
        "UPDATE usuarios SET nombre=?, telefono=?, direccion=? WHERE id=?",
        (nombre, telefono, direccion, user_id)
    )
    conn.commit()
    conn.close()

def cambiar_contrasena(user_id, nueva_contrasena):
    """Genera un nuevo hash y actualiza la contrasena del usuario."""
    nuevo_hash = bcrypt.hashpw(nueva_contrasena.encode(), bcrypt.gensalt()).decode()
    conn = get_db()
    conn.execute(
        "UPDATE usuarios SET contrasena_hash=? WHERE id=?",
        (nuevo_hash, user_id)
    )
    conn.commit()
    conn.close()

def listar_clientes(busqueda=''):
    """Lista todos los clientes. El admin usa esto para gestionar usuarios."""
    conn = get_db()
    if busqueda:
        clientes = conn.execute(
            "SELECT * FROM usuarios WHERE rol='cliente' AND (nombre LIKE ? OR email LIKE ?) ORDER BY nombre",
            (f'%{busqueda}%', f'%{busqueda}%')
        ).fetchall()
    else:
        clientes = conn.execute(
            "SELECT * FROM usuarios WHERE rol='cliente' ORDER BY nombre"
        ).fetchall()
    conn.close()
    return clientes

def eliminar_cliente(cliente_id):
    """Elimina un cliente de la base de datos."""
    conn = get_db()
    conn.execute("DELETE FROM usuarios WHERE id=? AND rol='cliente'", (cliente_id,))
    conn.commit()
    conn.close()

def contar_clientes():
    """Cuenta el total de clientes para el KPI del dashboard."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='cliente'").fetchone()[0]
    conn.close()
    return total
