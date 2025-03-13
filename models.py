from db import get_db_connection

def crear_tablas():
    conn = get_db_connection()
    cur = conn.cursor()

    # Tabla de productos con stock
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio DECIMAL(10,2) NOT NULL,
            stock INT NOT NULL DEFAULT 0
        );
    """)
    
    # Tabla de ventas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP DEFAULT current_timestamp,
            total DECIMAL(10,2) NOT NULL
        );
    """)
    
    # Tabla de detalles de venta
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalles_venta (
            id SERIAL PRIMARY KEY,
            venta_id INT REFERENCES ventas(id) ON DELETE CASCADE,
            producto_id INT REFERENCES productos(id),
            cantidad INT NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Tablas creadas o ya existían.")

def insertar_producto():
    conn = get_db_connection()
    cur = conn.cursor()

    # Insertar un producto de prueba
    cur.execute("""
        INSERT INTO productos (nombre, precio, stock) 
        VALUES (%s, %s, %s) 
        RETURNING id;
    """, ("Monitor 25 pulgadas", 620.75, 10))
    
    producto_id = cur.fetchone()[0]  # Obtener el ID del producto insertado
    conn.commit()
    print(f"Producto de prueba insertado con ID: {producto_id}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    insertar_producto()