"""
modelos/producto.py
Funciones de base de datos para el catalogo de productos:
CRUD completo, busqueda, generacion automatica de codigos.
"""
import base64
import unicodedata
from modelos.conexion import get_db

def normalizar_categoria(categoria):
    """
    Convierte la categoria a un prefijo limpio para el codigo:
    - Elimina tildes y caracteres especiales
    - Convierte a mayusculas
    - Quita espacios
    Ejemplos:
      'Electrónica' → 'ELECTRONICA'
      'Hogar'       → 'HOGAR'
      'Ropa'        → 'ROPA'
      'Tecnología'  → 'TECNOLOGIA'
    Esto garantiza que 'Hogar', 'HOGAR', 'hogar' y 'Hógar' 
    todos generen el mismo prefijo HOGAR y continuen la misma secuencia.
    """
    # Descompone los caracteres y elimina los acentos (NFD + filtro de categoria Mn)
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', categoria)
        if unicodedata.category(c) != 'Mn'
    )
    return sin_tildes.upper().replace(' ', '').replace('-', '')

def generar_codigo(categoria):
    """
    Genera el codigo automaticamente: CATEGORIA-XXX donde XXX es el
    siguiente numero disponible buscando en la BD cuantos productos
    ya existen con ese prefijo normalizado.

    Ejemplos:
      Si ya hay HOGAR-001 y HOGAR-002, el siguiente es HOGAR-003
      Si ya hay ELECTRONICA-001, el siguiente es ELECTRONICA-002
      Si no hay ninguno, empieza en 001
    """
    conn    = get_db()
    prefijo = normalizar_categoria(categoria)

    # Busca TODOS los productos cuyo codigo empiece con ese prefijo
    # Esto funciona aunque el usuario escriba 'hogar', 'Hogar' o 'HOGAR'
    existentes = conn.execute(
        "SELECT codigo FROM productos WHERE UPPER(REPLACE(codigo, ' ', '')) LIKE ?",
        (f'{prefijo}-%',)
    ).fetchall()
    conn.close()

    # Extrae el numero al final del codigo: HOGAR-002 → 2
    numeros = []
    for row in existentes:
        partes = row['codigo'].split('-')
        ultimo = partes[-1]
        if ultimo.isdigit():
            numeros.append(int(ultimo))

    # Siguiente = maximo actual + 1 (o 1 si no hay ninguno todavia)
    siguiente = (max(numeros) if numeros else 0) + 1
    return f"{prefijo}-{str(siguiente).zfill(3)}"

def crear(nombre, descripcion, precio, stock, categoria, archivo_imagen=None):
    """
    Crea un nuevo producto con codigo generado automaticamente.
    La imagen se convierte a base64 si el usuario sube una.
    """
    codigo = generar_codigo(categoria)

    imagen_url = None
    if archivo_imagen and archivo_imagen.filename:
        contenido  = archivo_imagen.read()
        mime       = archivo_imagen.content_type or 'image/jpeg'
        imagen_url = f"data:{mime};base64,{base64.b64encode(contenido).decode()}"

    conn = get_db()
    conn.execute(
        "INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria, imagen_url) VALUES (?,?,?,?,?,?,?)",
        (codigo, nombre, descripcion, precio, stock, categoria, imagen_url)
    )
    conn.commit()
    conn.close()
    return codigo

def obtener_por_id(producto_id):
    """Obtiene un producto por su id."""
    conn     = get_db()
    producto = conn.execute("SELECT * FROM productos WHERE id = ?", (producto_id,)).fetchone()
    conn.close()
    return producto

def listar_para_tienda(busqueda='', categoria=''):
    """Lista productos con stock > 0 para la tienda del cliente."""
    conn   = get_db()
    query  = "SELECT * FROM productos WHERE stock > 0"
    params = []

    if busqueda:
        query  += " AND (nombre LIKE ? OR descripcion LIKE ?)"
        params += [f'%{busqueda}%', f'%{busqueda}%']
    if categoria:
        query  += " AND categoria = ?"
        params.append(categoria)

    query     += " ORDER BY nombre"
    productos  = conn.execute(query, params).fetchall()
    categorias = conn.execute(
        "SELECT DISTINCT categoria FROM productos WHERE stock > 0 ORDER BY categoria"
    ).fetchall()
    conn.close()
    return productos, categorias

def listar_para_admin(busqueda='', categoria=''):
    """Lista TODOS los productos para el panel de administracion."""
    conn   = get_db()
    query  = "SELECT * FROM productos WHERE 1=1"
    params = []

    if busqueda:
        query  += " AND (nombre LIKE ? OR codigo LIKE ?)"
        params += [f'%{busqueda}%', f'%{busqueda}%']
    if categoria:
        query  += " AND categoria = ?"
        params.append(categoria)

    query     += " ORDER BY categoria, codigo"
    productos  = conn.execute(query, params).fetchall()
    categorias = conn.execute(
        "SELECT DISTINCT categoria FROM productos ORDER BY categoria"
    ).fetchall()
    conn.close()
    return productos, categorias

def actualizar(producto_id, nombre, descripcion, precio, stock, categoria,
               archivo_imagen=None, imagen_actual=None):
    """Actualiza los datos de un producto. Conserva la imagen si no se sube una nueva."""
    imagen_url = imagen_actual

    if archivo_imagen and archivo_imagen.filename:
        contenido  = archivo_imagen.read()
        mime       = archivo_imagen.content_type or 'image/jpeg'
        imagen_url = f"data:{mime};base64,{base64.b64encode(contenido).decode()}"

    conn = get_db()
    conn.execute(
        """UPDATE productos SET nombre=?, descripcion=?, precio=?,
           stock=?, categoria=?, imagen_url=? WHERE id=?""",
        (nombre, descripcion, precio, stock, categoria, imagen_url, producto_id)
    )
    conn.commit()
    conn.close()

def eliminar(producto_id):
    """
    Elimina el producto FISICAMENTE de la base de datos.
    Si tiene ventas asociadas lanza un error para proteger el historial.
    """
    conn = get_db()

    tiene_ventas = conn.execute(
        "SELECT COUNT(*) FROM detalle_ventas WHERE producto_id = ?", (producto_id,)
    ).fetchone()[0]

    if tiene_ventas > 0:
        conn.close()
        raise ValueError(
            f"No se puede eliminar: tiene {tiene_ventas} venta(s) registrada(s). "
            "Pon el stock en 0 para que no aparezca en la tienda."
        )

    conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()

def listar_stock_bajo():
    """Productos con 5 o menos unidades para la alerta del dashboard."""
    conn      = get_db()
    productos = conn.execute(
        "SELECT * FROM productos WHERE stock <= 5 ORDER BY stock"
    ).fetchall()
    conn.close()
    return productos

def contar_total():
    """Cuenta el total de productos para el KPI del dashboard."""
    conn  = get_db()
    total = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    conn.close()
    return total
