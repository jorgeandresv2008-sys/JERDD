"""
rutas/administrador.py
Rutas del panel de administracion: dashboard, productos, clientes, ventas.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import modelos.producto as Producto
import modelos.usuario  as Usuario
import modelos.venta    as Venta
from rutas.utilidades import requiere_admin, usuario_actual

administrador = Blueprint('administrador', __name__, url_prefix='/admin')


@administrador.route('/')
@administrador.route('/dashboard')
@requiere_admin
def dashboard():
    """Dashboard con KPIs calculados directamente desde la BD."""
    meses_nombres = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

    return render_template('admin/dashboard.html',
        total_productos = Producto.contar_total(),
        total_clientes  = Usuario.contar_clientes(),
        total_ventas    = Venta.contar_total(),
        ingresos        = Venta.sumar_ingresos(),
        stock_bajo      = Producto.listar_stock_bajo(),
        grafico_labels  = meses_nombres,
        grafico_datos   = Venta.ventas_por_mes(),
        usuario         = usuario_actual()
    )


# ── PRODUCTOS ──────────────────────────────────────────

@administrador.route('/productos')
@requiere_admin
def productos():
    busqueda  = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    prods, cats = Producto.listar_para_admin(busqueda, categoria)

    return render_template('admin/productos.html',
        productos=prods,
        categorias=cats,
        busqueda=busqueda,
        categoria=categoria,
        usuario=usuario_actual()
    )


@administrador.route('/productos/agregar', methods=['GET', 'POST'])
@requiere_admin
def agregar_producto():
    _, cats = Producto.listar_para_admin()

    if request.method == 'POST':
        nombre     = request.form.get('nombre', '').strip()
        categoria  = request.form.get('categoria', '').strip()
        precio_str = request.form.get('precio', '')
        stock_str  = request.form.get('stock', '')
        descripcion= request.form.get('descripcion', '').strip()

        # Valida campos obligatorios antes de crear el producto
        errores = []
        if not nombre:
            errores.append('El nombre es obligatorio.')
        if not categoria:
            errores.append('La categoria es obligatoria.')
        if not precio_str or float(precio_str) <= 0:
            errores.append('El precio debe ser mayor a 0.')
        if stock_str == '' or int(stock_str) < 0:
            errores.append('El stock no puede ser negativo.')

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('admin/agregar_producto.html',
                categorias=cats, usuario=usuario_actual())

        archivo = request.files.get('imagen')
        codigo  = Producto.crear(
            nombre, descripcion, float(precio_str),
            int(stock_str), categoria, archivo
        )
        flash(f'Producto creado con codigo {codigo}.', 'success')
        return redirect(url_for('administrador.productos'))

    return render_template('admin/agregar_producto.html',
        categorias=cats, usuario=usuario_actual())


@administrador.route('/productos/editar/<int:pid>', methods=['GET', 'POST'])
@requiere_admin
def editar_producto(pid):
    producto = Producto.obtener_por_id(pid)
    _, cats  = Producto.listar_para_admin()

    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('administrador.productos'))

    if request.method == 'POST':
        archivo = request.files.get('imagen')
        Producto.actualizar(
            pid,
            request.form['nombre'].strip(),
            request.form.get('descripcion', '').strip(),
            float(request.form['precio']),
            int(request.form['stock']),
            request.form['categoria'].strip(),
            archivo,
            producto['imagen_url']
        )
        flash('Producto actualizado.', 'success')
        return redirect(url_for('administrador.productos'))

    return render_template('admin/editar_producto.html',
        producto=producto, categorias=cats, usuario=usuario_actual())


@administrador.route('/productos/eliminar/<int:pid>', methods=['POST'])
@requiere_admin
def eliminar_producto(pid):
    """
    Elimina el producto fisicamente de la base de datos.
    Si tiene ventas asociadas muestra un mensaje de error explicativo.
    """
    try:
        Producto.eliminar(pid)
        flash('Producto eliminado correctamente.', 'success')
    except ValueError as e:
        # El modelo lanza ValueError si el producto tiene ventas asociadas
        flash(str(e), 'warning')

    return redirect(url_for('administrador.productos'))


# ── CLIENTES ───────────────────────────────────────────

@administrador.route('/clientes')
@requiere_admin
def clientes():
    busqueda = request.args.get('q', '')
    return render_template('admin/clientes.html',
        clientes=Usuario.listar_clientes(busqueda),
        busqueda=busqueda,
        usuario=usuario_actual()
    )


@administrador.route('/clientes/eliminar/<int:cid>', methods=['POST'])
@requiere_admin
def eliminar_cliente(cid):
    Usuario.eliminar_cliente(cid)
    flash('Cliente eliminado.', 'success')
    return redirect(url_for('administrador.clientes'))


# ── VENTAS ──────────────────────────────────────────────

@administrador.route('/ventas')
@requiere_admin
def ventas():
    fecha_ini = request.args.get('fecha_ini', '')
    fecha_fin = request.args.get('fecha_fin', '')
    return render_template('admin/ventas.html',
        ventas=Venta.listar_todas(fecha_ini, fecha_fin),
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin,
        usuario=usuario_actual()
    )


@administrador.route('/ventas/<int:venta_id>')
@requiere_admin
def ver_venta(venta_id):
    venta    = Venta.obtener_factura(venta_id)
    detalles = Venta.obtener_detalle(venta_id)
    return render_template('cliente/factura.html',
        venta=venta,
        detalles=detalles,
        cantidad_carrito=0,
        usuario=usuario_actual()
    )
