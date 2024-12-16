from db import connect
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import datetime
from fpdf import FPDF


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

            # Calcular I.G.V. y actualizar el total de la factura
            igv = subtotal * 0.18  # 18% I.G.V.
            total = subtotal + igv
            cursor.execute("UPDATE facturas SET total = %s WHERE id = %s", (total, factura_id))

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

            # Crear archivo PDF de factura
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Información de la factura
            pdf.cell(200, 10, txt=f"Factura ID: {factura[0]}", ln=True)
            pdf.cell(200, 10, txt=f"Cliente: {factura[1]}", ln=True)
            pdf.cell(200, 10, txt=f"Dirección: {factura[2]}", ln=True)
            pdf.cell(200, 10, txt=f"Teléfono: {factura[3]}", ln=True)
            pdf.cell(200, 10, txt=f"Fecha: {factura[4]}", ln=True)
            pdf.cell(200, 10, txt=f"Total: S/. {factura[5]:.2f}", ln=True)
            pdf.cell(200, 10, txt="Detalles de Factura:", ln=True)

            # Detalles de productos
            pdf.cell(100, 10, txt="Producto", border=1, align='C')
            pdf.cell(40, 10, txt="Cantidad", border=1, align='C')
            pdf.cell(40, 10, txt="Subtotal", border=1, align='C')
            pdf.ln()

            for detalle in detalles:
                pdf.cell(100, 10, txt=detalle[0], border=1)
                pdf.cell(40, 10, txt=str(detalle[1]), border=1)
                pdf.cell(40, 10, txt=f"S/. {detalle[2]:.2f}", border=1)
                pdf.ln()

            # Guardar PDF
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Guardar Factura")
            if file_path:
                pdf.output(file_path)

            messagebox.showinfo("Éxito", "Factura guardada exitosamente como PDF")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir la factura: {e}")

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

    # Campos para editar/eliminar una factura
    tk.Label(ventana_facturacion, text="ID Factura:").pack()
    entry_factura_id = tk.Entry(ventana_facturacion)
    entry_factura_id.pack()

    tk.Label(ventana_facturacion, text="Nuevo Total (opcional):").pack()
    entry_nuevo_total = tk.Entry(ventana_facturacion)
    entry_nuevo_total.pack()

    tk.Button(ventana_facturacion, text="Editar Factura", command=editar_factura).pack(pady=10)
    tk.Button(ventana_facturacion, text="Eliminar Factura", command=eliminar_factura).pack(pady=10)
    tk.Button(ventana_facturacion, text="Imprimir Factura (PDF)", command=imprimir_factura_pdf).pack(pady=10)

    # Listbox para mostrar las facturas
    listbox_facturas = tk.Listbox(ventana_facturacion, width=100, height=15)
    listbox_facturas.pack(pady=10)

    mostrar_facturas()
    ventana_facturacion.mainloop()