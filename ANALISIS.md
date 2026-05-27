# Análisis y Diseño del Sistema JERDD

## 1. Descripción del problema

El proyecto JERDD nace como solución a la necesidad de una **tienda virtual** que permita a clientes comprar productos en línea y a administradores gestionar el inventario, los clientes y las ventas desde un panel de control centralizado.

### Actores del sistema

| Actor | Descripción |
|---|---|
| **Cliente** | Usuario registrado que navega el catálogo, agrega productos al carrito y finaliza compras |
| **Administrador** | Usuario con rol `admin` que gestiona productos, clientes y revisa reportes |

---

## 2. Casos de uso principales

### Actor: Cliente
- Registrarse en el sistema
- Iniciar y cerrar sesión
- Navegar y filtrar el catálogo de productos
- Agregar productos al carrito (controlando stock)
- Actualizar cantidades o eliminar ítems del carrito
- Finalizar compra (genera factura automática con IVA del 19%)
- Consultar historial de compras
- Ver factura de una compra específica
- Actualizar datos del perfil
- Cambiar contraseña

### Actor: Administrador
- Ver dashboard con KPIs (productos, clientes, ventas, ingresos)
- Ver gráfico de ventas por mes
- Recibir alertas de stock bajo (≤ 5 unidades)
- Crear productos con código generado automáticamente
- Editar y eliminar productos
- Buscar y filtrar productos por nombre, código o categoría
- Ver y buscar clientes
- Eliminar clientes
- Ver listado de ventas con filtro por fecha
- Ver detalle de cualquier factura

---

## 3. Arquitectura: Patrón MVC

JERDD implementa el patrón **Modelo–Vista–Controlador** usando las herramientas de Flask:

```
Petición HTTP
      │
      ▼
  [Rutas / Blueprint]  ←── Controlador: recibe la petición, coordina
      │
      ├── llama a ──► [Modelos]  ←── Lógica de negocio + acceso a BD
      │                   │
      │                   └── ejecuta SQL ──► [SQLite]
      │
      └── renderiza ──► [Plantillas Jinja2]  ←── Vista: HTML al cliente
```

### Separación de responsabilidades

- **`modelos/`** encapsula toda la lógica SQL. Las rutas nunca escriben consultas directamente.
- **`rutas/`** contienen únicamente lógica de flujo HTTP (leer formulario → llamar modelo → redirigir o renderizar).
- **`plantillas/`** usan herencia de `base.html` para evitar repetir el navbar y los imports de CSS/JS.

---

## 4. Principios de POO aplicados

### Encapsulamiento
Cada módulo de `modelos/` encapsula su acceso a datos. Por ejemplo, `modelos/producto.py` expone funciones de alto nivel como `crear()`, `actualizar()` y `eliminar()`, ocultando los detalles de conexión SQL al resto del sistema.

```python
# Uso desde la ruta (no conoce SQL):
codigo = Producto.crear(nombre, descripcion, precio, stock, categoria, archivo)
```

### Abstracción
`get_db()` en `conexion.py` abstrae la apertura de la base de datos. Cualquier módulo que necesite una conexión llama esta función sin conocer el path del archivo ni la configuración de `row_factory`.

```python
def get_db():
    conn = sqlite3.connect('base_datos/jerdd.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

### Reutilización
Los decoradores `@requiere_login` y `@requiere_admin` en `utilidades.py` centralizan la lógica de autorización. En lugar de repetir la verificación de sesión en cada ruta, se aplican como decoradores:

```python
@administrador.route('/dashboard')
@requiere_admin   # <- reutilizado en todas las rutas del panel admin
def dashboard():
    ...
```

### Separación de responsabilidades (SRP)
Cada archivo tiene una sola razón para cambiar:
- `conexion.py` → si cambia el motor de base de datos
- `producto.py` → si cambia la lógica de productos
- `autenticacion.py` → si cambia el flujo de login

---

## 5. Modelo de datos

### Entidad: `usuarios`

| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| nombre | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| contrasena_hash | TEXT | NOT NULL (bcrypt) |
| rol | TEXT | 'admin' o 'cliente' |
| direccion | TEXT | Opcional |
| telefono | TEXT | Opcional |

### Entidad: `productos`

| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| codigo | TEXT | UNIQUE (ej: HOGAR-001) |
| nombre | TEXT | NOT NULL |
| descripcion | TEXT | Opcional |
| precio | REAL | NOT NULL |
| stock | INTEGER | DEFAULT 0 |
| categoria | TEXT | Para filtros |
| imagen_url | TEXT | Base64 o URL |

### Entidad: `ventas`

| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| numero_factura | TEXT | UNIQUE (FAC-YYYYMMDD-XXXX) |
| fecha | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| cliente_id | INTEGER | FK → usuarios |
| subtotal | REAL | NOT NULL |
| iva | REAL | 19% del subtotal |
| total | REAL | subtotal + iva |

### Entidad: `detalle_ventas`

| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| venta_id | INTEGER | FK → ventas |
| producto_id | INTEGER | FK → productos |
| cantidad | INTEGER | NOT NULL |
| precio_unitario | REAL | Precio al momento de la compra |

### Relaciones

- `usuarios` 1 → N `ventas` (un cliente puede tener muchas compras)
- `ventas` 1 → N `detalle_ventas` (una factura tiene varios ítems)
- `productos` 1 → N `detalle_ventas` (un producto puede aparecer en varios detalles)

---

## 6. Lógica de negocio destacada

### Generación automática de códigos de producto

El sistema genera códigos como `HOGAR-001`, `ELECTRONICA-003` automáticamente al crear un producto. El prefijo se normaliza (elimina tildes, mayúsculas) para garantizar consistencia:

```
'Electrónica' → ELECTRONICA
'Hogar'       → HOGAR
'Ropa de Mujer' → ROPAMUJER
```

### Seguridad de contraseñas

Las contraseñas nunca se guardan en texto plano. Se usa `bcrypt` que incorpora un *salt* aleatorio en cada hash:

```python
hash = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()
```

### Control de stock en el carrito

Al agregar un producto, el sistema verifica que la cantidad en carrito más la solicitada no supere el stock disponible. Al finalizar la compra, se hace una segunda verificación contra la BD y se descuenta el stock atómicamente.

### Protección del historial de ventas

Al intentar eliminar un producto que tiene ventas registradas, el sistema lanza un `ValueError` que la ruta captura y muestra como mensaje de advertencia, sin eliminar el producto. Esto protege la integridad del historial.

---

## 7. Seguridad implementada

| Mecanismo | Descripción |
|---|---|
| Hash de contraseñas | bcrypt con salt aleatorio |
| Control de sesión | Flask session con `secret_key` |
| Autorización por rol | Decoradores `@requiere_login` y `@requiere_admin` |
| Acceso a facturas | Solo el dueño o el admin puede ver una factura |
| Integridad referencial | `PRAGMA foreign_keys = ON` en SQLite |
| Validación de formularios | Validación en servidor antes de cualquier INSERT |

---

## 8. Flujo de una compra completa

```
Cliente en tienda
      │
      ▼
Agrega producto al carrito (POST /agregar_carrito)
  → Verifica stock
  → Guarda en session['carrito'] = {producto_id: cantidad}
      │
      ▼
Ve el carrito (GET /carrito)
  → Calcula subtotal, IVA, total
      │
      ▼
Finaliza compra (POST /finalizar_compra)
  → Re-verifica stock en BD
  → INSERT ventas (cabecera con número FAC-YYYYMMDD-XXXX)
  → INSERT detalle_ventas (una fila por ítem)
  → UPDATE stock de cada producto
  → session.pop('carrito')
  → Redirige a /factura/<venta_id>
      │
      ▼
Ve la factura generada
```
