from db import connect
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document  # Para generar documentos en Word

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
            messagebox.showerror("Error", "Por favor, ingresa el ID de la factura a imprimir en PDF")
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

            # Crear archivo PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivo PDF", "*.pdf")],
                title="Guardar Factura en PDF"
            )

            if not file_path:
                return

            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, f"Factura ID: {factura[0]}")
            c.drawString(100, 730, f"Cliente: {factura[1]}")
            c.drawString(100, 710, f"Dirección: {factura[2]}")
            c.drawString(100, 690, f"Teléfono: {factura[3]}")
            c.drawString(100, 670, f"Fecha: {factura[4]}")
            c.drawString(100, 650, f"Total: S/{factura[5]:.2f}")

            c.drawString(100, 620, "Detalles:")
            c.drawString(100, 600, "Producto       Cantidad    Subtotal")

            y = 580
            for detalle in detalles:
                c.drawString(100, y, f"{detalle[0]}       {detalle[1]}      S/{detalle[2]:.2f}")
                y -= 20

            c.save()
            messagebox.showinfo("Éxito", "Factura guardada exitosamente en PDF")

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
                    f"ID: {factura[0]}, Cliente: {factura[1]}, Fecha: {factura[2]}, Total: S/{factura[3]:.2f}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar las facturas: {e}")

    ventana_facturacion = tk.Toplevel()
    ventana_facturacion.title("Sistema de Facturación")
    ventana_facturacion.geometry("800x600")

    # Campos para generar una nueva factura
    tk.Label(ventana_facturacion, text="ID Cliente:").pack()
    entry_cliente_id = tk.Entry(ventana_facturacion)
    entry_cliente_id.pack()

    tk.Label(ventana_facturacion, text="ID Producto:").pack()
    entry_producto_id = tk.Entry(ventana_facturacion)
    entry_producto_id.pack()

    tk.Label(ventana_facturacion, text="Cantidad:").pack()
    entry_cantidad = tk.Entry(ventana_facturacion)
    entry_cantidad.pack()

    tk.Button(ventana_facturacion, text="Generar Factura", command=generar_factura).pack(pady=10)

    # Campos para editar/eliminar/imprimir una factura
    tk.Label(ventana_facturacion, text="ID Factura:").pack()
    entry_factura_id = tk.Entry(ventana_facturacion)
    entry_factura_id.pack()

    tk.Label(ventana_facturacion, text="Nuevo Total (opcional para editar):").pack()
    entry_nuevo_total = tk.Entry(ventana_facturacion)
    entry_nuevo_total.pack()

    tk.Button(ventana_facturacion, text="Editar Factura", command=editar_factura).pack(pady=10)
    tk.Button(ventana_facturacion, text="Eliminar Factura", command=eliminar_factura).pack(pady=10)
    tk.Button(ventana_facturacion, text="Imprimir Factura (PDF)", command=imprimir_factura_pdf).pack(pady=10)

    # Listbox para mostrar las facturas
    listbox_facturas = tk.Listbox(ventana_facturacion, width=100, height=20)
    listbox_facturas.pack(pady=20)

    tk.Button(ventana_facturacion, text="Actualizar Lista", command=mostrar_facturas).pack(pady=10)

    mostrar_facturas()
