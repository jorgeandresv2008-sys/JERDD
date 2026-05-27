"""
rutas/tienda.py
Rutas de la tienda para clientes: productos, carrito, compra, historial y perfil.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import modelos.producto as Producto
import modelos.venta    as Venta
import modelos.usuario  as Usuario
from rutas.utilidades import requiere_login, usuario_actual, cantidad_carrito

tienda = Blueprint('tienda', __name__)

@tienda.route('/tienda')
@requiere_login
def index():
    busqueda  = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    productos, categorias = Producto.listar_para_tienda(busqueda, categoria)

    return render_template('cliente/tienda.html',
        productos=productos,
        categorias=categorias,
        busqueda=busqueda,
        categoria=categoria,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )

@tienda.route('/agregar_carrito', methods=['POST'])
@requiere_login
def agregar_carrito():
    """
    Agrega un producto al carrito de la sesion.
    El carrito es un diccionario {producto_id: cantidad} guardado en session.
    """
    producto_id = request.form.get('producto_id', type=int)
    cantidad    = request.form.get('cantidad', 1, type=int)

    producto = Producto.obtener_por_id(producto_id)
    if not producto:
        return jsonify({'ok': False, 'mensaje': 'Producto no encontrado'}), 404

    # Lee el carrito de la sesion (o crea uno vacio)
    carrito   = session.get('carrito', {})
    clave     = str(producto_id)
    en_carrito = carrito.get(clave, 0)

    # Verifica que no supere el stock disponible
    if en_carrito + cantidad > producto['stock']:
        return jsonify({'ok': False, 'mensaje': f'Solo hay {producto["stock"]} unidades disponibles'}), 400

    carrito[clave] = en_carrito + cantidad
    session['carrito'] = carrito

    total_items = sum(carrito.values())
    return jsonify({'ok': True, 'mensaje': f'"{producto["nombre"]}" agregado', 'total': total_items})

@tienda.route('/carrito')
@requiere_login
def ver_carrito():
    """Construye la vista del carrito leyendo los ids de la sesion y buscando en BD."""
    carrito_sesion = session.get('carrito', {})
    items    = []
    subtotal = 0

    for producto_id, cant in carrito_sesion.items():
        producto = Producto.obtener_por_id(int(producto_id))
        if producto:
            sub = producto['precio'] * cant
            items.append({'producto': producto, 'cantidad': cant, 'subtotal': sub})
            subtotal += sub

    iva   = round(subtotal * 0.19, 2)
    total = round(subtotal + iva, 2)

    return render_template('cliente/carrito.html',
        items=items,
        subtotal=subtotal,
        iva=iva,
        total=total,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )

@tienda.route('/actualizar_carrito', methods=['POST'])
@requiere_login
def actualizar_carrito():
    producto_id = request.form.get('producto_id')
    nueva_cant  = request.form.get('cantidad', type=int)
    carrito = session.get('carrito', {})

    if nueva_cant and nueva_cant > 0:
        carrito[producto_id] = nueva_cant
    else:
        carrito.pop(producto_id, None)

    session['carrito'] = carrito
    return redirect(url_for('tienda.ver_carrito'))

@tienda.route('/eliminar_del_carrito', methods=['POST'])
@requiere_login
def eliminar_del_carrito():
    producto_id = request.form.get('producto_id')
    carrito = session.get('carrito', {})
    carrito.pop(producto_id, None)
    session['carrito'] = carrito
    return redirect(url_for('tienda.ver_carrito'))

@tienda.route('/finalizar_compra', methods=['POST'])
@requiere_login
def finalizar_compra():
    """
    Procesa la compra completa:
    1. Valida stock de cada producto
    2. Registra la venta y el detalle en la BD
    3. Descuenta el stock
    4. Vacia el carrito de la sesion
    """
    carrito_sesion = session.get('carrito', {})
    if not carrito_sesion:
        flash('El carrito esta vacio.', 'warning')
        return redirect(url_for('tienda.ver_carrito'))

    # Reconstruye los items verificando stock real en la BD
    items = []
    for producto_id, cantidad in carrito_sesion.items():
        producto = Producto.obtener_por_id(int(producto_id))
        if not producto:
            continue
        if producto['stock'] < cantidad:
            flash(f'Stock insuficiente para "{producto["nombre"]}".', 'danger')
            return redirect(url_for('tienda.ver_carrito'))
        items.append({'producto': producto, 'cantidad': cantidad})

    # Crea la venta en la base de datos
    venta_id, numero = Venta.crear_venta(session['usuario_id'], items)

    # Vacia el carrito de la sesion tras compra exitosa
    session.pop('carrito', None)
    flash(f'Compra exitosa! Factura: {numero}', 'success')
    return redirect(url_for('tienda.factura', venta_id=venta_id))

@tienda.route('/mis_compras')
@requiere_login
def mis_compras():
    compras = Venta.listar_por_cliente(session['usuario_id'])
    return render_template('cliente/mis_compras.html',
        compras=compras,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )

@tienda.route('/factura/<int:venta_id>')
@requiere_login
def factura(venta_id):
    venta    = Venta.obtener_factura(venta_id)
    detalles = Venta.obtener_detalle(venta_id)

    # Solo el dueno de la factura o el admin puede verla
    if not venta or (venta['cliente_id'] != session['usuario_id']
                     and session.get('usuario_rol') != 'admin'):
        flash('Factura no encontrada.', 'danger')
        return redirect(url_for('tienda.mis_compras'))

    return render_template('cliente/factura.html',
        venta=venta,
        detalles=detalles,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )

@tienda.route('/perfil', methods=['GET', 'POST'])
@requiere_login
def perfil():
    u = usuario_actual()
    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'datos':
            Usuario.actualizar_datos(
                session['usuario_id'],
                request.form['nombre'].strip(),
                request.form.get('telefono', '').strip(),
                request.form.get('direccion', '').strip()
            )
            session['usuario_nombre'] = request.form['nombre'].strip()
            flash('Datos actualizados.', 'success')

        elif accion == 'contrasena':
            actual  = request.form['contrasena_actual']
            nueva   = request.form['contrasena_nueva']
            nueva2  = request.form['contrasena_nueva2']

            if not Usuario.verificar_contrasena(u['contrasena_hash'], actual):
                flash('La contrasena actual es incorrecta.', 'danger')
            elif nueva != nueva2:
                flash('Las contrasenas nuevas no coinciden.', 'danger')
            elif len(nueva) < 6:
                flash('La nueva contrasena debe tener al menos 6 caracteres.', 'danger')
            else:
                Usuario.cambiar_contrasena(session['usuario_id'], nueva)
                flash('Contrasena cambiada exitosamente.', 'success')

        return redirect(url_for('tienda.perfil'))

    return render_template('cliente/perfil.html',
        usuario=u,
        cantidad_carrito=cantidad_carrito()
    )
