from db import connect
import tkinter as tk
from tkinter import messagebox

def gestionar_productos():
    def agregar_producto():
        nombre = entry_nombre.get()
        precio = entry_precio.get()
        stock = entry_stock.get()

        if not nombre or not precio or not stock:
            messagebox.showerror("Error", "Por favor, completa todos los campos")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, precio, stock))
            db.commit()
            db.close()
            messagebox.showinfo("Éxito", "Producto agregado exitosamente")
            mostrar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

    def editar_producto():
        producto_id = entry_id.get()
        nombre = entry_nombre.get()
        precio = entry_precio.get()
        stock = entry_stock.get()

        if not producto_id:
            messagebox.showerror("Error", "Por favor, ingresa el ID del producto a editar")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = """
                UPDATE productos
                SET nombre = %s, precio = %s, stock = %s
                WHERE id = %s
            """
            cursor.execute(query, (nombre, precio, stock, producto_id))
            db.commit()
            db.close()
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Producto editado exitosamente")
            else:
                messagebox.showwarning("Advertencia", "No se encontró un producto con ese ID")
            mostrar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar el producto: {e}")

    def eliminar_producto():
        producto_id = entry_id.get()

        if not producto_id:
            messagebox.showerror("Error", "Por favor, ingresa el ID del producto a eliminar")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "DELETE FROM productos WHERE id = %s"
            cursor.execute(query, (producto_id,))
            db.commit()
            db.close()
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Producto eliminado exitosamente")
            else:
                messagebox.showwarning("Advertencia", "No se encontró un producto con ese ID")
            mostrar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

    def mostrar_productos():
        try:
            db = connect()
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre, precio, stock FROM productos")
            resultados = cursor.fetchall()
            db.close()
            listbox_productos.delete(0, tk.END)
            for producto in resultados:
                listbox_productos.insert(
                    tk.END,
                    f"ID: {producto[0]}, Nombre: {producto[1]}, Precio: S/{producto[2]:.2f}, Stock: {producto[3]}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la lista de productos: {e}")

    ventana_productos = tk.Toplevel()
    ventana_productos.title("Gestión de Productos")
    ventana_productos.geometry("800x600")

    # Campos para datos del producto
    tk.Label(ventana_productos, text="ID Producto (para editar/eliminar):").pack()
    entry_id = tk.Entry(ventana_productos)
    entry_id.pack()

    tk.Label(ventana_productos, text="Nombre:").pack()
    entry_nombre = tk.Entry(ventana_productos)
    entry_nombre.pack()

    tk.Label(ventana_productos, text="Precio (en soles):").pack()
    entry_precio = tk.Entry(ventana_productos)
    entry_precio.pack()

    tk.Label(ventana_productos, text="Stock:").pack()
    entry_stock = tk.Entry(ventana_productos)
    entry_stock.pack()

    # Botones para gestionar productos
    tk.Button(ventana_productos, text="Agregar Producto", command=agregar_producto).pack(pady=10)
    tk.Button(ventana_productos, text="Editar Producto", command=editar_producto).pack(pady=10)
    tk.Button(ventana_productos, text="Eliminar Producto", command=eliminar_producto).pack(pady=10)

    # Listbox para mostrar productos
    listbox_productos = tk.Listbox(ventana_productos, width=100, height=20)
    listbox_productos.pack(pady=20)

    tk.Button(ventana_productos, text="Actualizar Lista", command=mostrar_productos).pack(pady=10)

    mostrar_productos()
