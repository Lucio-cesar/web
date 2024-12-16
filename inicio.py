import tkinter as tk
from tkinter import filedialog, messagebox
from db import connect
import subprocess
from PIL import Image, ImageTk

# Función para encriptar y desencriptar colores
def encriptar_color(color):
    # Simple encriptación, cambiar la primera y última letra
    return color[::-1]  # Solo para fines de ejemplo, un método muy simple

def desencriptar_color(color_encriptado):
    return color_encriptado[::-1]

# Colores "encriptados" para la UI
color_fondo = encriptar_color("#aed6f1")  # azul pálido
color_texto = encriptar_color("#060606")  # negro
color_button = encriptar_color("#58f14e")  # Verde

# Función para registrar una nueva cuenta
def registrar_cuenta():
    def registrar():
        usuario = entry_usuario.get()
        contrasena = entry_contrasena.get()
        rol = combo_rol.get()
        foto_ruta = label_foto_path.cget("text")

        if not usuario or not contrasena or rol == "Selecciona un rol" or foto_ruta == "No se seleccionó una foto":
            messagebox.showerror("Error", "Por favor, completa todos los campos y selecciona una foto")
            return

        try:
            db = connect()
            cursor = db.cursor()
            query = "INSERT INTO usuarios (usuario, contrasena, rol, foto) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (usuario, contrasena, rol, foto_ruta))
            db.commit()
            db.close()
            messagebox.showinfo("Éxito", "Cuenta registrada exitosamente")
            ventana_registro.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la cuenta: {e}")

    # Crear la ventana de registro
    ventana_registro = tk.Toplevel(ventana_principal)
    ventana_registro.title("Registrar Nueva Cuenta")
    ventana_registro.geometry("350x400")
    ventana_registro.configure(bg=desencriptar_color(color_fondo))  # Desencriptar color de fondo

    # Usuario
    tk.Label(ventana_registro, text="Usuario:", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=5)
    entry_usuario = tk.Entry(ventana_registro)
    entry_usuario.pack(pady=5)

    # Contraseña
    tk.Label(ventana_registro, text="Contraseña:", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=5)
    entry_contrasena = tk.Entry(ventana_registro, show="*")
    entry_contrasena.pack(pady=5)

    # Rol
    tk.Label(ventana_registro, text="Rol:", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=5)
    combo_rol = tk.StringVar(value="Selecciona un rol")
    tk.OptionMenu(ventana_registro, combo_rol, "administrador", "usuario").pack(pady=5)

    # Foto
    tk.Label(ventana_registro, text="Foto de perfil:", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=5)
    label_foto_path = tk.Label(ventana_registro, text="No se seleccionó una foto", fg="gray")
    label_foto_path.pack(pady=5)

    def cargar_foto():
        # Abrir un cuadro de diálogo para seleccionar una foto
        archivo = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if archivo:
            label_foto_path.config(text=archivo)  # Mostrar la ruta de la foto seleccionada

    # Botón para cargar la foto
    tk.Button(ventana_registro, text="Seleccionar Foto", command=cargar_foto, bg=desencriptar_color(color_button)).pack(pady=5)

    # Botón para registrar
    tk.Button(ventana_registro, text="Registrar", command=registrar, bg=desencriptar_color(color_button)).pack(pady=10)


# Función para autenticar usuarios
def autenticar_usuario():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    if not usuario or not contrasena:
        messagebox.showerror("Error", "Por favor, completa todos los campos")
        return

    try:
        db = connect()
        cursor = db.cursor()
        query = "SELECT rol, foto FROM usuarios WHERE usuario = %s AND contrasena = %s"
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        db.close()

        if resultado:
            rol, foto_ruta = resultado
            messagebox.showinfo("Éxito", f"Bienvenido, {usuario} ({rol})")
            ventana_principal.destroy()
            subprocess.run(["python", "interface.py", usuario, rol, foto_ruta])  # Pasar nombre, rol y foto
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo autenticar: {e}")


# Configuración de la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Sistema de Facturación")
ventana_principal.geometry("400x300")
ventana_principal.configure(bg=desencriptar_color(color_fondo))  # Desencriptar color de fondo

# Usuario
tk.Label(ventana_principal, text="Usuario:", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=5)
entry_usuario = tk.Entry(ventana_principal)
entry_usuario.pack(pady=5)

# Contraseña
tk.Label(ventana_principal, text="Contraseña:", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=5)
entry_contrasena = tk.Entry(ventana_principal, show="*")
entry_contrasena.pack(pady=5)

# Botón para ingresar
tk.Button(ventana_principal, text="Ingresar", command=autenticar_usuario, bg=desencriptar_color(color_button)).pack(pady=10)

# Botón para registrar nueva cuenta
tk.Button(ventana_principal, text="Registrar Nueva Cuenta", command=registrar_cuenta, bg=desencriptar_color(color_button)).pack(pady=10)

ventana_principal.mainloop()
