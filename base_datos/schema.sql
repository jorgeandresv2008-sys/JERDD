CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL,
    direccion TEXT,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    categoria TEXT,
    imagen_url TEXT
);

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT UNIQUE NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cliente_id INTEGER NOT NULL,
    subtotal REAL NOT NULL,
    iva REAL NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
