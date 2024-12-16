import matplotlib.pyplot as plt
from db import connect

def generar_grafico():
    try:
        db = connect()
        cursor = db.cursor()
        query = """
            SELECT DATE(fecha) AS dia, SUM(total) AS total_dia
            FROM facturas
            GROUP BY DATE(fecha)
            ORDER BY DATE(fecha)
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        db.close()

        fechas = [r[0].strftime('%Y-%m-%d') for r in resultados]
        totales = [r[1] for r in resultados]

        plt.figure(figsize=(10, 6))
        plt.plot(fechas, totales, marker='o')
        plt.title("Ventas Diarias")
        plt.xlabel("Fecha")
        plt.ylabel("Total de Ventas")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error al generar el gráfico: {e}")
