-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS sistema_facturacion;
USE sistema_facturacion;

-- Tabla para usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(100) NOT NULL,
    rol ENUM('administrador', 'usuario') NOT NULL,
    foto VARCHAR(255)  -- Columna para la imagen del usuario
);

-- Tabla para clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    correo VARCHAR(100),
    foto VARCHAR(255)  -- Columna para la imagen del cliente
);

-- Tabla para productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL CHECK (stock >= 0)
);

-- Tabla para facturas
CREATE TABLE IF NOT EXISTS facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- Tabla para detalles de facturas
CREATE TABLE IF NOT EXISTS detalles_factura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

-- Insertar usuario inicial (Administrador)
INSERT INTO usuarios (usuario, contrasena, rol, foto)
VALUES 
('lucio', 'cesar', 'administrador', 'usuarios/lucio.png')
ON DUPLICATE KEY UPDATE usuario=usuario;

-- Insertar datos iniciales para clientes
INSERT INTO clientes (nombre, direccion, telefono, correo, foto)
VALUES 
('Juan Pérez', 'Calle 123', '555-1234', 'juan.perez@example.com', 'clientes/juan_perez.png'),
('María López', 'Avenida 456', '555-5678', 'maria.lopez@example.com', 'clientes/maria_lopez.png');

-- Insertar datos iniciales para productos
INSERT INTO productos (nombre, precio, stock)
VALUES 
('Laptop', 1200.00, 10),
('Mouse', 25.50, 50),
('Teclado', 45.00, 30),
('Monitor', 200.00, 15);

-- Ejemplo de inserción de una factura
INSERT INTO facturas (cliente_id, total)
VALUES 
(1, 1200.00);  -- Factura para el cliente con id=1 (Juan Pérez)

-- Insertar detalles de factura (Ejemplo)
INSERT INTO detalles_factura (factura_id, producto_id, cantidad, subtotal)
VALUES 
(1, 1, 1, 1200.00),  -- 1 Laptop para la factura con id=1
(1, 2, 1, 25.50);    -- 1 Mouse para la factura con id=1
