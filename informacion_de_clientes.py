import tkinter as tk
from tkinter import ttk, messagebox
from db import connect
from PIL import Image, ImageTk
import os

def mostrar_info_clientes():
    # Crear una ventana para mostrar los detalles de los clientes
    ventana_info = tk.Toplevel()
    ventana_info.title("Información de Clientes")
    ventana_info.geometry("800x600")
    
    # Etiqueta para el título
    tk.Label(ventana_info, text="Información de Clientes", font=("Arial", 16)).pack(pady=10)

    # Crear el Treeview para mostrar los datos de los clientes
    columns = ("ID", "Nombre", "Dirección", "Teléfono", "Correo", "Foto")
    treeview = ttk.Treeview(ventana_info, columns=columns, show="headings")

    # Definir las columnas
    treeview.heading("ID", text="ID")
    treeview.heading("Nombre", text="Nombre")
    treeview.heading("Dirección", text="Dirección")
    treeview.heading("Teléfono", text="Teléfono")
    treeview.heading("Correo", text="Correo")
    treeview.heading("Foto", text="Foto")

    # Ajustar el tamaño de las columnas
    treeview.column("ID", width=50, anchor="center")
    treeview.column("Nombre", width=150, anchor="w")
    treeview.column("Dirección", width=200, anchor="w")
    treeview.column("Teléfono", width=100, anchor="center")
    treeview.column("Correo", width=150, anchor="w")
    treeview.column("Foto", width=100, anchor="center")

    treeview.pack(pady=20, fill="both", expand=True)

    # Etiqueta para mostrar la foto del cliente seleccionado
    label_foto = tk.Label(ventana_info)
    label_foto.pack(pady=10)

    # Función para cargar los datos de la base de datos
    def cargar_clientes():
        try:
            db = connect()
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre, direccion, telefono, correo, foto FROM clientes")
            resultados = cursor.fetchall()
            db.close()

            # Limpiar el Treeview antes de insertar nuevos datos
            for row in treeview.get_children():
                treeview.delete(row)

            # Insertar los datos en el Treeview
            for cliente in resultados:
                cliente_id = cliente[0]
                nombre = cliente[1]
                direccion = cliente[2]
                telefono = cliente[3]
                correo = cliente[4]
                foto_ruta = cliente[5]

                # Mostrar los datos del cliente en el Treeview
                if foto_ruta:
                    treeview.insert("", "end", values=(cliente_id, nombre, direccion, telefono, correo, "Foto cargada"))
                else:
                    treeview.insert("", "end", values=(cliente_id, nombre, direccion, telefono, correo, "No foto"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la lista de clientes: {e}")

    # Llamar a la función para cargar los clientes
    cargar_clientes()

    # Función para mostrar la información completa de un cliente al hacer clic
    def mostrar_detalles_cliente(event):
        # Obtener el ID del cliente seleccionado
        item = treeview.selection()
        if not item:
            return
        cliente_id = treeview.item(item, "values")[0]  # Obtener el ID del cliente

        try:
            db = connect()
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre, direccion, telefono, correo, foto FROM clientes WHERE id = %s", (cliente_id,))
            cliente = cursor.fetchone()
            db.close()

            if cliente:
                cliente_id = cliente[0]
                nombre = cliente[1]
                direccion = cliente[2]
                telefono = cliente[3]
                correo = cliente[4]
                foto_ruta = cliente[5]

                # Mostrar los detalles del cliente
                messagebox.showinfo("Detalles del Cliente", 
                                    f"ID: {cliente_id}\nNombre: {nombre}\nDirección: {direccion}\nTeléfono: {telefono}\nCorreo: {correo}")

                # Mostrar la foto si existe
                if foto_ruta and os.path.exists(foto_ruta):  # Verificar si la foto existe
                    img = Image.open(foto_ruta)
                    img = img.resize((150, 150))  # Redimensionar la imagen
                    img = ImageTk.PhotoImage(img)

                    label_foto.config(image=img)
                    label_foto.image = img  # Mantener la referencia de la imagen
                    label_foto.pack(pady=10)
                else:
                    label_foto.config(image="")
                    label_foto.image = None
                    label_foto.pack_forget()
                    messagebox.showinfo("Foto no disponible", "Este cliente no tiene foto disponible.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la información del cliente: {e}")

    # Asociar la función de mostrar detalles del cliente al hacer clic en el Treeview
    treeview.bind("<ButtonRelease-1>", mostrar_detalles_cliente)

    # Botón para actualizar la lista de clientes
    tk.Button(ventana_info, text="Actualizar Lista", command=cargar_clientes).pack(pady=10)

    ventana_info.mainloop()
