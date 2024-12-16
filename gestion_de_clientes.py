from db import connect
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

def gestionar_clientes():
    def agregar_cliente():
        nombre = entry_nombre.get()
        direccion = entry_direccion.get()
        telefono = entry_telefono.get()
        correo = entry_correo.get()
        foto_ruta = label_foto_path.cget("text")  # Obtener la ruta de la foto

        if not nombre or not direccion or not telefono:
            messagebox.showerror("Error", "Por favor, completa todos los campos obligatorios")
            return

        # Si la foto no ha sido seleccionada
        if foto_ruta == "No se seleccionó una foto":
            messagebox.showerror("Error", "Por favor, selecciona una foto")
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

    def editar_cliente():
        cliente_id = entry_id.get()
        nombre = entry_nombre.get()
        direccion = entry_direccion.get()
        telefono = entry_telefono.get()
        correo = entry_correo.get()
        foto_ruta = label_foto_path.cget("text")  # Obtener la ruta de la foto

        if not cliente_id:
            messagebox.showerror("Error", "Por favor, ingresa el ID del cliente a editar")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = """
                UPDATE clientes 
                SET nombre = %s, direccion = %s, telefono = %s, correo = %s, foto = %s
                WHERE id = %s
            """
            cursor.execute(query, (nombre, direccion, telefono, correo, foto_ruta, cliente_id))
            db.commit()
            db.close()
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Cliente editado exitosamente")
            else:
                messagebox.showwarning("Advertencia", "No se encontró un cliente con ese ID")
            mostrar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar el cliente: {e}")

    def eliminar_cliente():
        cliente_id = entry_id.get()

        if not cliente_id:
            messagebox.showerror("Error", "Por favor, ingresa el ID del cliente a eliminar")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "DELETE FROM clientes WHERE id = %s"
            cursor.execute(query, (cliente_id,))
            db.commit()
            db.close()
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Cliente eliminado exitosamente")
            else:
                messagebox.showwarning("Advertencia", "No se encontró un cliente con ese ID")
            mostrar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")

    def mostrar_clientes():
        try:
            db = connect()
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre, direccion, telefono, correo, foto FROM clientes")
            resultados = cursor.fetchall()
            db.close()
            listbox_clientes.delete(0, tk.END)
            for cliente in resultados:
                # Mostrar solo el nombre y teléfono, no la foto
                listbox_clientes.insert(
                    tk.END,
                    f"ID: {cliente[0]}, Nombre: {cliente[1]}, Dirección: {cliente[2]}, Teléfono: {cliente[3]}, Correo: {cliente[4]}, Foto: {cliente[5]}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la lista de clientes: {e}")

    def cargar_foto():
        archivo = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if archivo:
            label_foto_path.config(text=archivo)  # Mostrar la ruta de la foto seleccionada
            # Mostrar la imagen seleccionada en una etiqueta
            try:
                img = Image.open(archivo)
                img = img.resize((100, 100))  # Redimensionar la imagen
                img = ImageTk.PhotoImage(img)
                label_foto.config(image=img)
                label_foto.image = img  # Mantener la referencia
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    # Función para ver clientes (abre la ventana de información_de_clientes.py)
    def ver_clientes():
        # Aquí debes definir cómo se abrirá la ventana de información de clientes
        # Asumiendo que la función `informacion_de_clientes()` está definida en otro archivo
        # Solo un ejemplo, para abrir la ventana de información de clientes
        import informacion_de_clientes
        informacion_de_clientes.mostrar_info_clientes()

    ventana_clientes = tk.Toplevel()
    ventana_clientes.title("Gestión de Clientes")
    ventana_clientes.geometry("900x900")

    # Campos para datos del cliente
    tk.Label(ventana_clientes, text="ID Cliente (para editar/eliminar):").pack()
    entry_id = tk.Entry(ventana_clientes)
    entry_id.pack()

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

    # Foto
    tk.Label(ventana_clientes, text="Foto de Perfil:").pack(pady=5)
    label_foto = tk.Label(ventana_clientes)
    label_foto.pack(pady=10)

    label_foto_path = tk.Label(ventana_clientes, text="No se seleccionó una foto", fg="gray")
    label_foto_path.pack(pady=5)

    # Botón para cargar la foto
    tk.Button(ventana_clientes, text="Seleccionar Foto", command=cargar_foto).pack(pady=5)

    # Botones para gestionar clientes
    tk.Button(ventana_clientes, text="Agregar Cliente", command=agregar_cliente).pack(pady=10)
    tk.Button(ventana_clientes, text="Editar Cliente", command=editar_cliente).pack(pady=10)
    tk.Button(ventana_clientes, text="Eliminar Cliente", command=eliminar_cliente).pack(pady=10)

    # Botón para ver los clientes
    tk.Button(ventana_clientes, text="Ver Clientes", command=ver_clientes).pack(pady=10)

    # Listbox para mostrar clientes
    listbox_clientes = tk.Listbox(ventana_clientes, width=100, height=20)
    listbox_clientes.pack(pady=20)

    tk.Button(ventana_clientes, text="Actualizar Lista", command=mostrar_clientes).pack(pady=10)

    mostrar_clientes()
