import mysql.connector

def connect():
    """Conectar a la base de datos."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="76272180",  # Cambia según tu configuración
        database="sistema_facturacion",
        port=33065  # Cambia el puerto si es necesario
    )
