from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    rol = db.Column(db.String(20), default='usuario')
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_negocio = db.Column(db.String(100), default='Ovni Burger')
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    nit = db.Column(db.String(20))
    instagram = db.Column(db.String(100))
    mensaje_pie = db.Column(db.String(200))
    whatsapp_default = db.Column(db.String(20))
    costo_domicilio = db.Column(db.Integer, default=3000)
    pedido_minimo = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    icono = db.Column(db.String(50))
    orden = db.Column(db.Integer, default=0)
    activa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Integer, default=0)
    categoria = db.Column(db.String(50))
    imagen = db.Column(db.String(300))
    stock = db.Column(db.Integer, default=100)
    disponible = db.Column(db.Boolean, default=True)
    highlighted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Mesa(db.Model):
    __tablename__ = 'mesas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True)
    capacidad = db.Column(db.Integer, default=4)
    estado = db.Column(db.String(20), default='libre')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sugerencia(db.Model):
    __tablename__ = 'sugerencias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    tipo = db.Column(db.String(20), default='sugerencia')
    mensaje = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    leida = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)