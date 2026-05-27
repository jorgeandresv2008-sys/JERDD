[README.md](https://github.com/user-attachments/files/28294529/README.md)
#  JERDD – Tienda Virtual

> Proyecto ABPr – Aplicación web de e-commerce desarrollada con Flask y Python  
> Programación Orientada a Objetos · SQLite · Arquitectura MVC

---

##  Descripción

**JERDD** es una tienda virtual completa desarrollada como proyecto final del semestre. Permite a los clientes explorar productos, gestionar un carrito de compras y generar facturas, mientras que el administrador puede controlar el inventario, ver estadísticas y gestionar usuarios desde un panel dedicado.

La aplicación aplica los principios de **Programación Orientada a Objetos** organizando la lógica en módulos separados por responsabilidad (modelos, rutas, plantillas), y usa **Blueprints de Flask** para estructurar el código de forma escalable.

---

##  Estructura del Proyecto

```
JERDD/
│
├── app.py                        # Punto de entrada – configura Flask y registra blueprints
├── seed.py                       # Carga datos de ejemplo en la base de datos
│
├── modelos/                      # Capa de acceso a datos (lógica de negocio + BD)
│   ├── conexion.py               # Conexión SQLite y función de inicialización
│   ├── producto.py               # CRUD completo de productos + generación de códigos
│   ├── usuario.py                # Registro, login, perfil y gestión de clientes
│   └── venta.py                  # Registro de ventas, facturas y estadísticas
│
├── rutas/                        # Controladores (blueprints Flask)
│   ├── autenticacion.py          # Login, registro y logout
│   ├── administrador.py          # Panel de admin: productos, clientes, ventas
│   ├── tienda.py                 # Tienda cliente: catálogo, carrito, compra, perfil
│   └── utilidades.py             # Decoradores de autorización y funciones auxiliares
│
├── plantillas/                   # Vistas HTML (Jinja2)
│   ├── base.html                 # Plantilla base con navbar compartido
│   ├── login.html
│   ├── registro.html
│   ├── admin/                    # Vistas del panel de administración
│   │   ├── dashboard.html
│   │   ├── productos.html
│   │   ├── agregar_producto.html
│   │   ├── editar_producto.html
│   │   ├── clientes.html
│   │   └── ventas.html
│   └── cliente/                  # Vistas de la tienda del cliente
│       ├── tienda.html
│       ├── carrito.html
│       ├── factura.html
│       ├── mis_compras.html
│       └── perfil.html
│
├── estatico/
│   └── css/style.css             # Estilos personalizados
│
└── base_datos/
    ├── schema.sql                # Definición de tablas SQL
    └── jerdd.db                  # Base de datos SQLite (generada al ejecutar)
```

---

##  Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/JERDD.git
cd JERDD
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

pip install flask bcrypt
```

### 3. Cargar datos de ejemplo

```bash
python seed.py
```

### 4. Ejecutar la aplicación

```bash
python app.py
```

Abre tu navegador en: **http://localhost:5000**

---

##  Credenciales de prueba

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | admin@jerdd.com | admin123 |
| Cliente | juan@test.com | cliente123 |
| Cliente | maria@test.com | cliente123 |
| Cliente | carlos@test.com | cliente123 |

---

##  Funcionalidades

### Panel del Cliente
- **Registro e inicio de sesión** con contraseñas hasheadas con bcrypt
- **Catálogo de productos** con filtros por categoría y búsqueda
- **Carrito de compras** persistente en sesión, con control de stock
- **Finalización de compra** con generación automática de factura (IVA 19%)
- **Historial de compras** y visualización de facturas
- **Perfil de usuario** con actualización de datos y cambio de contraseña

### Panel del Administrador
- **Dashboard** con KPIs: total de productos, clientes, ventas e ingresos
- **Gráfico de ventas por mes**
- **Alertas de stock bajo** (productos con ≤ 5 unidades)
- **CRUD completo de productos** con carga de imagen y código automático por categoría
- **Gestión de clientes** con búsqueda y eliminación
- **Reporte de ventas** con filtro por rango de fechas

---

##  Arquitectura y POO

El proyecto aplica los principios de **Programación Orientada a Objetos** y el patrón **MVC** de la siguiente forma:

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| **Modelo** | `modelos/` | Encapsula toda la lógica de acceso a datos. Cada módulo (`producto.py`, `usuario.py`, `venta.py`) agrupa las operaciones relacionadas con una entidad. |
| **Vista** | `plantillas/` | Plantillas Jinja2 que presentan los datos al usuario. Herencia de plantillas desde `base.html`. |
| **Controlador** | `rutas/` | Blueprints Flask que reciben las peticiones HTTP, invocan los modelos y devuelven las vistas. |

### Principios aplicados

- **Encapsulamiento**: cada módulo de `modelos/` oculta los detalles de la conexión SQL y expone funciones de alto nivel (`crear`, `actualizar`, `eliminar`).
- **Separación de responsabilidades**: las rutas no contienen lógica SQL; los modelos no conocen Flask ni HTTP.
- **Reutilización**: los decoradores `@requiere_login` y `@requiere_admin` en `utilidades.py` centralizan la autorización para todas las rutas.
- **Abstracción**: `get_db()` en `conexion.py` abstrae la apertura de la BD; `generar_codigo()` en `producto.py` encapsula la lógica de codificación automática.

---

##  Modelo de Datos

```
usuarios
  id, nombre, email, contrasena_hash, rol, direccion, telefono

productos
  id, codigo (CATEGORIA-NNN), nombre, descripcion, precio, stock, categoria, imagen_url

ventas
  id, numero_factura (FAC-YYYYMMDD-XXXX), fecha, cliente_id → usuarios, subtotal, iva, total

detalle_ventas
  id, venta_id → ventas, producto_id → productos, cantidad, precio_unitario
```

---

##  Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3 | Lenguaje principal |
| Flask | Framework web (rutas, sesiones, plantillas) |
| SQLite | Base de datos relacional |
| bcrypt | Hash seguro de contraseñas |
| Jinja2 | Motor de plantillas HTML |
| Bootstrap 5 | Estilos y componentes UI |

---

##  Integrantes del grupo

| Nombre | Rol |
|---|---|
| Jorge Vergara - Ronald Ochoa | Desarrollo backend |
| Jorge Vergara - Ronald Ochoa | Desarrollo frontend |

---

##  Licencia

Proyecto académico – Programación Orientada a Objetos
