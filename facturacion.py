import tkinter as tk
from tkinter import messagebox, filedialog
from db import connect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

def gestionar_facturacion():
    def generar_factura():
        cliente_id = entry_cliente_id.get()
        producto_id = entry_producto_id.get()
        cantidad = entry_cantidad.get()

        if not cliente_id or not producto_id or not cantidad:
            messagebox.showerror("Error", "Por favor, completa todos los campos")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a cero")
                return

            db = connect()
            cursor = db.cursor()

            # Verificar si el producto existe y obtener su precio y stock
            cursor.execute("SELECT stock, precio FROM productos WHERE id = %s", (producto_id,))
            producto = cursor.fetchone()

            if not producto:
                messagebox.showerror("Error", "Producto no encontrado")
                return

            stock, precio = producto
            if cantidad > stock:
                messagebox.showerror("Error", "No hay suficiente stock para esta cantidad")
                return

            # Crear la factura
            cursor.execute("INSERT INTO facturas (cliente_id, total) VALUES (%s, 0)", (cliente_id,))
            factura_id = cursor.lastrowid

            # Calcular subtotal y agregar al detalle de la factura
            subtotal = cantidad * precio
            cursor.execute(
                "INSERT INTO detalles_factura (factura_id, producto_id, cantidad, subtotal) VALUES (%s, %s, %s, %s)",
                (factura_id, producto_id, cantidad, subtotal)
            )

            # Actualizar el stock del producto
            cursor.execute("UPDATE productos SET stock = stock - %s WHERE id = %s", (cantidad, producto_id))

            # Actualizar el total de la factura
            cursor.execute("UPDATE facturas SET total = total + %s WHERE id = %s", (subtotal, factura_id))

            db.commit()
            db.close()

            messagebox.showinfo("Éxito", f"Factura generada exitosamente (ID: {factura_id})")
            mostrar_facturas()

        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")

    def editar_factura():
        factura_id = entry_factura_id.get()
        nuevo_total = entry_nuevo_total.get()

        if not factura_id or not nuevo_total:
            messagebox.showerror("Error", "Por favor, completa todos los campos")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "UPDATE facturas SET total = %s WHERE id = %s"
            cursor.execute(query, (nuevo_total, factura_id))
            db.commit()
            db.close()

            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Factura editada exitosamente")
            else:
                messagebox.showwarning("Advertencia", "No se encontró una factura con ese ID")
            mostrar_facturas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar la factura: {e}")

    def eliminar_factura():
        factura_id = entry_factura_id.get()

        if not factura_id:
            messagebox.showerror("Error", "Por favor, ingresa el ID de la factura a eliminar")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "DELETE FROM facturas WHERE id = %s"
            cursor.execute(query, (factura_id,))
            db.commit()
            db.close()

            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Factura eliminada exitosamente")
            else:
                messagebox.showwarning("Advertencia", "No se encontró una factura con ese ID")
            mostrar_facturas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la factura: {e}")

    def imprimir_factura_pdf():
        factura_id = entry_factura_id.get()

        if not factura_id:
            messagebox.showerror("Error", "Por favor, ingresa el ID de la factura a imprimir")
            return

        try:
            db = connect()
            cursor = db.cursor()

            # Obtener los detalles de la factura
            query_factura = """
                SELECT f.id, c.nombre, c.direccion, c.telefono, f.fecha, f.total
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                WHERE f.id = %s
            """
            cursor.execute(query_factura, (factura_id,))
            factura = cursor.fetchone()

            if not factura:
                messagebox.showwarning("Advertencia", "No se encontró una factura con ese ID")
                return

            query_detalles = """
                SELECT p.nombre, df.cantidad, df.subtotal
                FROM detalles_factura df
                JOIN productos p ON df.producto_id = p.id
                WHERE df.factura_id = %s
            """
            cursor.execute(query_detalles, (factura_id,))
            detalles = cursor.fetchall()
            db.close()

            # Crear el archivo PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Guardar Factura como PDF"
            )

            if not file_path:
                return

            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 10)

            # Escribir la factura en el PDF
            c.drawString(50, 750, f"COMPANIA LCL USRL S.A.C. - RUC 7627218010")
            c.drawString(50, 735, f"CAL. CESAR LOPEZ 181 P - 3, JULIACA, PUNO")
            c.drawString(50, 720, f"BOLETA DE VENTA ELECTRONICA BA52-06606576")
            c.drawString(50, 705, f"CAJERO : 1")
            c.drawString(50, 690, f"SUB: S/.  {factura[5]:.2f}")
            c.drawString(50, 675, f"I.G.V.: %. 18")
            c.drawString(50, 660, f"IMPORTE TOTAL: S/. {factura[5]:.2f}")
            c.drawString(50, 645, f"TOTAL A PAGAR: S/. {factura[5]:.2f}")
            c.drawString(50, 630, f"SOLES")
            c.drawString(50, 615, f"VUELTO: S/. 0.00")
            c.drawString(50, 600, "--------------------------------------------")
            c.drawString(50, 585, f"FACTURA ID: {factura[0]}")
            c.drawString(50, 570, f"CLIENTE: {factura[1]}")
            c.drawString(50, 555, f"DIRECCION: {factura[2]}")
            c.drawString(50, 540, f"TELEFONO: {factura[3]}")
            c.drawString(50, 525, f"FECHA: {factura[4]}")
            c.drawString(50, 510, f"HORA: {datetime.datetime.now().strftime('%H:%M:%S')}")
            c.drawString(50, 495, "--------------------")
            c.drawString(50, 480, "DETALLES DE FACTURA:")

            y_position = 465  # Iniciar la posición Y para los detalles

            for detalle in detalles:
                c.drawString(50, y_position, f"Producto: {detalle[0]}")
                y_position -= 15
                c.drawString(50, y_position, f"Cantidad: {detalle[1]}")
                y_position -= 15
                c.drawString(50, y_position, f"Subtotal: S/. {detalle[2]:.2f}")
                y_position -= 30  # Separación entre productos

            c.save()

            messagebox.showinfo("Éxito", "Factura PDF generada exitosamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir la factura en PDF: {e}")

    def mostrar_facturas():
        try:
            db = connect()
            cursor = db.cursor()

            # Obtener las facturas con detalles del cliente
            query = """
                SELECT f.id, c.nombre, f.fecha, f.total
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                ORDER BY f.fecha DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            db.close()

            listbox_facturas.delete(0, tk.END)
            for factura in resultados:
                listbox_facturas.insert(
                    tk.END,
                    f"ID: {factura[0]}, Cliente: {factura[1]}, Fecha: {factura[2]}, Total: S/. {factura[3]:.2f}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar las facturas: {e}")

    # Ventana principal
    ventana = tk.Tk()
    ventana.title("Gestión de Facturación")

    # Campos de entrada
    tk.Label(ventana, text="ID Cliente:").grid(row=0, column=0, padx=10, pady=5)
    entry_cliente_id = tk.Entry(ventana)
    entry_cliente_id.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana, text="ID Producto:").grid(row=1, column=0, padx=10, pady=5)
    entry_producto_id = tk.Entry(ventana)
    entry_producto_id.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Cantidad:").grid(row=2, column=0, padx=10, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.grid(row=2, column=1, padx=10, pady=5)

    tk.Button(ventana, text="Generar Factura", command=generar_factura).grid(row=3, column=0, columnspan=2, pady=10)

    tk.Label(ventana, text="ID Factura:").grid(row=4, column=0, padx=10, pady=5)
    entry_factura_id = tk.Entry(ventana)
    entry_factura_id.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Nuevo Total (opcional):").grid(row=5, column=0, padx=10, pady=5)
    entry_nuevo_total = tk.Entry(ventana)
    entry_nuevo_total.grid(row=5, column=1, padx=10, pady=5)

    tk.Button(ventana, text="Editar Factura", command=editar_factura).grid(row=6, column=0, columnspan=2, pady=5)
    tk.Button(ventana, text="Eliminar Factura", command=eliminar_factura).grid(row=7, column=0, columnspan=2, pady=5)
    tk.Button(ventana, text="Imprimir Factura (PDF)", command=imprimir_factura_pdf).grid(row=8, column=0, columnspan=2, pady=5)

    # Listado de facturas
    listbox_facturas = tk.Listbox(ventana, width=50, height=10)
    listbox_facturas.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    mostrar_facturas()

    ventana.mainloop()
