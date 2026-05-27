"""
seed.py - Carga datos de ejemplo en la base de datos JERDD.
Ejecutar una sola vez: python seed.py
"""
import sqlite3
import bcrypt
import os

os.makedirs('base_datos', exist_ok=True)

conn = sqlite3.connect('base_datos/jerdd.db')

# Crea las tablas leyendo el schema.sql
with open('base_datos/schema.sql', encoding='utf-8') as f:
    conn.executescript(f.read())

def h(pwd):
    """Convierte una contrasena a hash bcrypt."""
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

# ── Usuarios ────────────────────────────────────────────
usuarios = [
    ('Admin JERDD',    'admin@jerdd.com',  h('admin123'),   'admin',   'Oficina Central',    '+57 1 234 5678'),
    ('Juan Perez',     'juan@test.com',    h('cliente123'), 'cliente', 'Calle 45 Medellin',  '+57 300 111 2222'),
    ('Maria Lopez',    'maria@test.com',   h('cliente123'), 'cliente', 'Carrera 7 Bogota',   '+57 311 333 4444'),
    ('Carlos Ruiz',    'carlos@test.com',  h('cliente123'), 'cliente', 'Av 6 Cali',          '+57 315 555 6666'),
]

for nombre, email, pwd, rol, dir_, tel in usuarios:
    try:
        conn.execute(
            "INSERT INTO usuarios (nombre,email,contrasena_hash,rol,direccion,telefono) VALUES(?,?,?,?,?,?)",
            (nombre, email, pwd, rol, dir_, tel)
        )
        print(f"  Usuario: {email}")
    except sqlite3.IntegrityError:
        print(f"  Ya existe: {email}")

# ── Productos con codigos usando categoria completa ──────
# El codigo usa la categoria COMPLETA en mayusculas: ELECTRONICA-001, ROPA-001, HOGAR-001
productos = [
    ('ELECTRONICA-001', 'Laptop Ultradelgada',  'Intel i5 8GB RAM 256GB SSD',        2850000, 15, 'Electronica', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400'),
    ('ELECTRONICA-002', 'Smartphone Pro Max',   'AMOLED 6.7 pulgadas 128GB 5G',      1950000, 30, 'Electronica', 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400'),
    ('ELECTRONICA-003', 'Audifonos Bluetooth',  'Cancelacion de ruido 30h bateria',   385000, 50, 'Electronica', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'),
    ('ELECTRONICA-004', 'Tablet 10 pulgadas',   'Pantalla IPS 64GB WiFi Bluetooth',   980000, 20, 'Electronica', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400'),
    ('ROPA-001',        'Camiseta Premium',      '100 algodon pima corte slim fit',     89000,100, 'Ropa',        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'),
    ('ROPA-002',        'Zapatillas Running',    'Suela EVA upper respirable',         320000, 40, 'Ropa',        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
    ('HOGAR-001',       'Cafetera Espresso',     '15 bares deposito 1.8 litros',       750000, 12, 'Hogar',       'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400'),
    ('HOGAR-002',       'Set de Sartenes',       '3 piezas antiadherentes induccion',  185000,  4, 'Hogar',       'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400'),
]

for cod, nom, desc, precio, stock, cat, img in productos:
    try:
        conn.execute(
            "INSERT INTO productos (codigo,nombre,descripcion,precio,stock,categoria,imagen_url) VALUES(?,?,?,?,?,?,?)",
            (cod, nom, desc, precio, stock, cat, img)
        )
        print(f"  Producto [{cod}]: {nom}")
    except sqlite3.IntegrityError:
        print(f"  Ya existe: {cod}")

conn.commit()
conn.close()

print("\nBase de datos lista!")
print("  Admin:   admin@jerdd.com  / admin123")
print("  Cliente: juan@test.com    / cliente123")
print("\nEjecuta: python app.py")
print("Abre:    http://localhost:5000")
