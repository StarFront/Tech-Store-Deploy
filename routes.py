from flask import Blueprint, request, jsonify, send_file
from db import get_db_connection
import pandas as pd
import io


routes = Blueprint('routes', __name__)

# Obtener todos los productos
@routes.route('/productos', methods=['GET'])
def obtener_productos():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM productos;")
    productos = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([{"id": p[0], "nombre": p[1], "precio": float(p[2]), "stock": p[3]} for p in productos])



# Agregar un producto
@routes.route('/productos', methods=['POST'])
def agregar_producto():
    datos = request.json
    nombre = datos.get("nombre")
    precio = datos.get("precio")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO productos (nombre, precio) VALUES (%s, %s) RETURNING id;", (nombre, precio))
    nuevo_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"mensaje": "Producto agregado", "id": nuevo_id}), 201

# Actualizar un producto
@routes.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    datos = request.json
    nombre = datos.get("nombre")
    precio = datos.get("precio")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE productos SET nombre = %s, precio = %s WHERE id = %s RETURNING id;", (nombre, precio, id))
    actualizado = cur.fetchone()

    if actualizado:
        conn.commit()
        mensaje = {"mensaje": "Producto actualizado"}
    else:
        mensaje = {"error": "Producto no encontrado"}

    cur.close()
    conn.close()

    return jsonify(mensaje)

# Eliminar un producto
@routes.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM productos WHERE id = %s RETURNING id;", (id,))
    eliminado = cur.fetchone()

    if eliminado:
        conn.commit()
        mensaje = {"mensaje": "Producto eliminado"}
    else:
        mensaje = {"error": "Producto no encontrado"}

    cur.close()
    conn.close()

    return jsonify(mensaje)

@routes.route('/factura', methods=['POST'])
def generar_factura():
    datos = request.json
    productos_vendidos = datos.get("productos", [])

    if not productos_vendidos:
        return jsonify({"error": "No se enviaron productos"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Verificar si hay suficiente stock
    for producto in productos_vendidos:
        cur.execute("SELECT stock FROM productos WHERE id = %s;", (producto["id"],))
        resultado = cur.fetchone()
        if not resultado or resultado[0] < producto["cantidad"]:
            cur.close()
            conn.close()
            return jsonify({"error": f"Stock insuficiente para el producto ID {producto['id']}"}), 400

    # Insertar venta en la tabla ventas
    cur.execute("INSERT INTO ventas (total) VALUES (0) RETURNING id;")
    venta_id = cur.fetchone()[0]

    total_venta = 0

    # Insertar detalles de venta y actualizar stock
    for producto in productos_vendidos:
        cur.execute("SELECT precio FROM productos WHERE id = %s;", (producto["id"],))
        precio = cur.fetchone()[0]
        subtotal = precio * producto["cantidad"]
        total_venta += subtotal

        cur.execute("""
            INSERT INTO detalles_venta (venta_id, producto_id, cantidad, subtotal) 
            VALUES (%s, %s, %s, %s);
        """, (venta_id, producto["id"], producto["cantidad"], subtotal))

        cur.execute("""
            UPDATE productos 
            SET stock = stock - %s 
            WHERE id = %s;
        """, (producto["cantidad"], producto["id"]))

    # Actualizar el total de la venta
    cur.execute("UPDATE ventas SET total = %s WHERE id = %s;", (total_venta, venta_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "mensaje": "Factura generada con éxito",
        "venta_id": venta_id,
        "total": total_venta
    }), 201

# Generar y descargar reporte de ventas en XLS
@routes.route('/reporte_ventas', methods=['GET'])
def reporte_ventas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id, v.fecha, v.total, p.nombre, d.cantidad, d.subtotal 
        FROM ventas v
        JOIN detalles_venta d ON v.id = d.venta_id
        JOIN productos p ON d.producto_id = p.id;
    """)
    datos = cur.fetchall()
    cur.close()
    conn.close()
    
    # Crear DataFrame de pandas
    df = pd.DataFrame(datos, columns=["Venta ID", "Fecha", "Total", "Producto", "Cantidad", "Subtotal"])
    
    # Guardar en un archivo en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Reporte Ventas", index=False)
    output.seek(0)
    
    return send_file(output, download_name="reporte_ventas.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")