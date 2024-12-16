import tkinter as tk
from PIL import Image, ImageTk
from gestion_de_clientes import gestionar_clientes
from gestion_de_productos import gestionar_productos
from facturacion import gestionar_facturacion
from grafico_de_ventas import generar_grafico

# Función para encriptar y desencriptar colores
def encriptar_color(color):
    return color[::-1]

def desencriptar_color(color_encriptado):
    return color_encriptado[::-1]

# Colores "encriptados" para la UI
color_fondo = encriptar_color("#f4f6f6")  # sombra muy claro de cian
color_texto = encriptar_color("#060606")  # Negro
color_button = encriptar_color("#f4d03f")  # sombra claro medio de amarillo

def abrir_gestion_clientes():
    gestionar_clientes()

def abrir_gestion_productos():
    gestionar_productos()

def abrir_facturacion():
    gestionar_facturacion()

def abrir_grafico_ventas():
    generar_grafico()

def mostrar_usuario(rol, usuario, foto_ruta):
    # Mostrar el rol y el nombre del usuario
    label_rol = tk.Label(ventana_facturacion, text=f"Bienvenido, {usuario} ({rol})", bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto))
    label_rol.pack(pady=10)

    # Mostrar la foto del usuario
    try:
        img = Image.open(foto_ruta)
        img = img.resize((100, 100))  # Redimensionar la foto para que quepa bien
        img = ImageTk.PhotoImage(img)
        label_foto = tk.Label(ventana_facturacion, image=img)
        label_foto.image = img  # Mantener la referencia para que no se libere
        label_foto.pack(pady=10)
    except Exception as e:
        print(f"No se pudo cargar la imagen: {e}")

# Configuración de la ventana de facturación
ventana_facturacion = tk.Tk()
ventana_facturacion.title("Sistema de Facturación")
ventana_facturacion.geometry("500x550")
ventana_facturacion.configure(bg=desencriptar_color(color_fondo))  # Desencriptar color de fondo

# Obtener los argumentos (usuario, rol y ruta de la foto)
import sys
usuario = sys.argv[1]  # Obtiene el nombre de usuario de los argumentos pasados
rol = sys.argv[2]      # Obtiene el rol del usuario
foto_ruta = sys.argv[3]  # Obtiene la ruta de la foto

# Mostrar la información del usuario
mostrar_usuario(rol, usuario, foto_ruta)

# Mostrar las opciones del sistema
tk.Label(ventana_facturacion, text="Menú Principal", font=("Arial", 16, "bold"), bg=desencriptar_color(color_fondo), fg=desencriptar_color(color_texto)).pack(pady=20)

tk.Button(ventana_facturacion, text="Gestión de Clientes", command=abrir_gestion_clientes, bg=desencriptar_color(color_button), width=30).pack(pady=10)
tk.Button(ventana_facturacion, text="Gestión de Productos", command=abrir_gestion_productos, bg=desencriptar_color(color_button), width=30).pack(pady=10)
tk.Button(ventana_facturacion, text="Facturación", command=abrir_facturacion, bg=desencriptar_color(color_button), width=30).pack(pady=10)
tk.Button(ventana_facturacion, text="Gráfico de Ventas", command=abrir_grafico_ventas, bg=desencriptar_color(color_button), width=30).pack(pady=10)

tk.Button(ventana_facturacion, text="Salir", command=ventana_facturacion.destroy, bg=desencriptar_color(color_button), width=30).pack(pady=10)

ventana_facturacion.mainloop()
