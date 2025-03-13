import psycopg2
import urllib.parse as urlparse
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("cockroachdb://", "postgresql://")
url = urlparse.urlparse(DATABASE_URL)

def get_db_connection():
    return psycopg2.connect(
        dbname=url.path[1:],  
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        sslmode="verify-full"
    )
