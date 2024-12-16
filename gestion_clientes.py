from db import connect
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def gestionar_clientes():
    def agregar_cliente():
        nombre = entry_nombre.get()
        direccion = entry_direccion.get()
        telefono = entry_telefono.get()
        correo = entry_correo.get()
        foto_ruta = label_foto_path.cget("text")  # Obtener la ruta de la foto seleccionada

        if not nombre or not direccion or not telefono:
            messagebox.showerror("Error", "Por favor, completa todos los campos obligatorios")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "INSERT INTO clientes (nombre, direccion, telefono, correo, foto) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nombre, direccion, telefono, correo, foto_ruta))
            db.commit()
            db.close()
            messagebox.showinfo("Éxito", "Cliente agregado exitosamente")
            mostrar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el cliente: {e}")

    def mostrar_clientes():
        try:
            db = connect()
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre, direccion, telefono, foto FROM clientes")
            resultados = cursor.fetchall()
            db.close()
            listbox_clientes.delete(0, tk.END)
            for cliente in resultados:
                listbox_clientes.insert(
                    tk.END,
                    f"ID: {cliente[0]}, Nombre: {cliente[1]}, Dirección: {cliente[2]}, Teléfono: {cliente[3]}, Foto: {cliente[4]}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la lista de clientes: {e}")

    def cargar_foto():
        archivo = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if archivo:
            label_foto_path.config(text=archivo)  # Mostrar la ruta de la foto seleccionada

    ventana_clientes = tk.Toplevel()
    ventana_clientes.title("Gestión de Clientes")
    ventana_clientes.geometry("700x600")  # Ajustamos el tamaño para incluir más campos

    tk.Label(ventana_clientes, text="Nombre:").pack()
    entry_nombre = tk.Entry(ventana_clientes)
    entry_nombre.pack()

    tk.Label(ventana_clientes, text="Dirección:").pack()
    entry_direccion = tk.Entry(ventana_clientes)
    entry_direccion.pack()

    tk.Label(ventana_clientes, text="Teléfono:").pack()
    entry_telefono = tk.Entry(ventana_clientes)
    entry_telefono.pack()

    tk.Label(ventana_clientes, text="Correo:").pack()
    entry_correo = tk.Entry(ventana_clientes)
    entry_correo.pack()

    # Campo para seleccionar la foto
    tk.Label(ventana_clientes, text="Foto (opcional):").pack()
    label_foto_path = tk.Label(ventana_clientes, text="No se seleccionó una foto", fg="gray")
    label_foto_path.pack(pady=5)

    # Botón para cargar la foto
    tk.Button(ventana_clientes, text="Seleccionar Foto", command=cargar_foto).pack(pady=10)

    # Botón para agregar el cliente
    tk.Button(ventana_clientes, text="Agregar Cliente", command=agregar_cliente).pack(pady=10)

    # Lista de clientes
    listbox_clientes = tk.Listbox(ventana_clientes, width=100, height=20)
    listbox_clientes.pack(pady=20)

    # Botón para actualizar la lista de clientes
    tk.Button(ventana_clientes, text="Actualizar Lista", command=mostrar_clientes).pack(pady=10)

    mostrar_clientes()

