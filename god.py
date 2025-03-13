import psycopg2
import urllib.parse as urlparse
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("cockroachdb://", "postgresql://")
url = urlparse.urlparse(DATABASE_URL)

conn = psycopg2.connect(
    dbname=url.path[1:],  
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode="verify-full"
)

cur = conn.cursor()

# Crear una tabla si no existe
# cur.execute("""
#     CREATE TABLE IF NOT EXISTS productos (
#         id SERIAL PRIMARY KEY,
#         nombre TEXT NOT NULL,
#         precio DECIMAL(10,2) NOT NULL
#     );
# """)
# conn.commit()

print("Tabla creada o ya existía.")

cur.close()
conn.close()

# def insertar_producto(nombre, precio):
#     conn = psycopg2.connect(
#         dbname=url.path[1:],  
#         user=url.username,
#         password=url.password,
#         host=url.hostname,
#         port=url.port,
#         sslmode="verify-full"
#     )
#     cur = conn.cursor()
    
#     cur.execute("INSERT INTO productos (nombre, precio) VALUES (%s, %s);", (nombre, precio))
    
#     conn.commit()
#     print(f"Producto '{nombre}' agregado con éxito.")
    
#     cur.close()
#     conn.close()

# # Insertar ejemplos
# insertar_producto("Laptop HP", 2500.99)
# insertar_producto("Mouse Logitech", 150.50)
