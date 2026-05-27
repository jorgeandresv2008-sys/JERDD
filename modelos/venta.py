"""
modelos/venta.py
Funciones de base de datos para ventas y facturas.
"""
from datetime import datetime
from modelos.conexion import get_db

def generar_numero_factura():
    """
    Genera un numero de factura con formato FAC-YYYYMMDD-XXXX.
    El correlativo se calcula contando las facturas del dia actual.
    """
    conn   = get_db()
    fecha  = datetime.now().strftime('%Y%m%d')
    n_hoy  = conn.execute(
        "SELECT COUNT(*) FROM ventas WHERE numero_factura LIKE ?",
        (f'FAC-{fecha}%',)
    ).fetchone()[0]
    conn.close()
    return f"FAC-{fecha}-{str(n_hoy + 1).zfill(4)}"

def crear_venta(cliente_id, items_carrito):
    """
    Registra una venta completa:
    1. INSERT en ventas (cabecera)
    2. INSERT en detalle_ventas (una fila por producto)
    3. UPDATE stock de cada producto vendido
    Retorna el id de la venta y el numero de factura.
    """
    conn = get_db()

    # Calcula subtotal, IVA y total
    subtotal = sum(i['producto']['precio'] * i['cantidad'] for i in items_carrito)
    iva      = round(subtotal * 0.19, 2)
    total    = round(subtotal + iva, 2)
    numero   = generar_numero_factura()

    # INSERT en la tabla ventas (cabecera de la factura)
    cursor   = conn.execute(
        "INSERT INTO ventas (numero_factura, cliente_id, subtotal, iva, total) VALUES (?,?,?,?,?)",
        (numero, cliente_id, subtotal, iva, total)
    )
    venta_id = cursor.lastrowid

    for item in items_carrito:
        # INSERT en detalle_ventas para cada producto comprado
        conn.execute(
            "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario) VALUES (?,?,?,?)",
            (venta_id, item['producto']['id'], item['cantidad'], item['producto']['precio'])
        )
        # Descuenta el stock del producto despues de la venta
        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (item['cantidad'], item['producto']['id'])
        )

    conn.commit()
    conn.close()
    return venta_id, numero

def obtener_factura(venta_id):
    """Obtiene la cabecera de una venta con datos del cliente (JOIN)."""
    conn   = get_db()
    venta  = conn.execute(
        """SELECT v.*, u.nombre as cliente_nombre, u.email as cliente_email,
                  u.direccion as cliente_direccion
           FROM ventas v JOIN usuarios u ON v.cliente_id = u.id
           WHERE v.id = ?""", (venta_id,)
    ).fetchone()
    conn.close()
    return venta

def obtener_detalle(venta_id):
    """Obtiene las lineas de detalle de una venta con nombre del producto (JOIN)."""
    conn     = get_db()
    detalles = conn.execute(
        """SELECT dv.*, p.nombre, p.codigo
           FROM detalle_ventas dv JOIN productos p ON dv.producto_id = p.id
           WHERE dv.venta_id = ?""", (venta_id,)
    ).fetchall()
    conn.close()
    return detalles

def listar_por_cliente(cliente_id):
    """Historial de compras de un cliente ordenado por fecha descendente."""
    conn    = get_db()
    compras = conn.execute(
        "SELECT * FROM ventas WHERE cliente_id = ? ORDER BY fecha DESC", (cliente_id,)
    ).fetchall()
    conn.close()
    return compras

def listar_todas(fecha_ini='', fecha_fin=''):
    """Lista todas las ventas con nombre del cliente. Admite filtros de fecha."""
    conn   = get_db()
    query  = """SELECT v.*, u.nombre as cliente_nombre, u.email as cliente_email
                FROM ventas v JOIN usuarios u ON v.cliente_id = u.id WHERE 1=1"""
    params = []

    if fecha_ini:
        query += " AND DATE(v.fecha) >= ?"
        params.append(fecha_ini)
    if fecha_fin:
        query += " AND DATE(v.fecha) <= ?"
        params.append(fecha_fin)

    query  += " ORDER BY v.fecha DESC"
    ventas  = conn.execute(query, params).fetchall()
    conn.close()
    return ventas

def contar_total():
    """Cuenta el total de ventas para el KPI del dashboard."""
    conn  = get_db()
    total = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    conn.close()
    return total

def sumar_ingresos():
    """Suma el total de ingresos para el KPI del dashboard."""
    conn     = get_db()
    ingresos = conn.execute("SELECT COALESCE(SUM(total),0) FROM ventas").fetchone()[0]
    conn.close()
    return ingresos

def ventas_por_mes():
    """Agrupa ingresos por mes para el grafico de barras del dashboard."""
    conn       = get_db()
    resultados = conn.execute(
        """SELECT strftime('%m', fecha) as mes, COALESCE(SUM(total), 0) as total
           FROM ventas GROUP BY strftime('%m', fecha) ORDER BY mes"""
    ).fetchall()
    conn.close()

    # Construye una lista de 12 valores (uno por mes)
    datos = [0.0] * 12
    for row in resultados:
        datos[int(row['mes']) - 1] = float(row['total'])
    return datos
