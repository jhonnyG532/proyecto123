from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, Usuario
import time
import re

auth_bp = Blueprint('auth', __name__)

# Rate limiting por IP
login_attempts = {}

def sanitize_input(text):
    """Sanitizar entrada de usuario"""
    if not text:
        return None
    # Solo permitir caracteres seguros
    return re.sub(r'[^\w\-.]', '', text)

def check_rate_limit(ip):
    """Verificar rate limiting por IP"""
    key = f"login:{ip}"
    now = time.time()
    if key in login_attempts:
        attempts, first_attempt = login_attempts[key]
        if now - first_attempt < 300:  # 5 minutos
            if attempts >= 5:
                return False
            login_attempts[key] = (attempts + 1, first_attempt)
        else:
            login_attempts[key] = (1, now)
    else:
        login_attempts[key] = (1, now)
    return True

def get_client_ip():
    """Obtener IP real del cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Endpoint de login con seguridad"""
    ip = get_client_ip()
    
    # Verificar rate limit
    if not check_rate_limit(ip):
        return jsonify({
            "error": "Demasiados intentos. Intenta en 5 minutos"
        }), 429
    
    # Obtener y sanitizar datos
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    username = sanitize_input(data.get('username', ''))
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    
    # Validar longitud
    if len(username) < 2 or len(username) > 50:
        return jsonify({"error": "Usuario inválido"}), 400
    
    # Buscar usuario
    usuario = Usuario.query.filter_by(username=username).first()
    
    if usuario and usuario.check_password(password):
        # Login exitoso - resetear intentos
        login_attempts.pop(f"login:{ip}", None)
        
        # Crear token JWT
        access_token = create_access_token(
            identity=username,
            additional_claims={"rol": usuario.rol}
        )
        
        return jsonify({
            "access_token": access_token,
            "username": username,
            "message": "Login exitoso"
        }), 200
    
    # Login fallido
    return jsonify({
        "error": "Credenciales inválidas"
    }), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    return jsonify({"message": "Sesión cerrada"}), 200

# Rutas protegidas
@auth_bp.route('/api/registro', methods=['POST'])
@jwt_required()
def registro():
    """Crear nuevo usuario (solo admin)"""
    current_user = get_jwt_identity()
    if current_user != 'jhonny':
        return jsonify({"error": "No autorizado"}), 403
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    username = sanitize_input(data.get('username', ''))
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    
    if len(password) < 4:
        return jsonify({"error": "Contraseña muy corta"}), 400
    
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error": "El usuario ya existe"}), 400
    
    nuevo_usuario = Usuario(username=username)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify({"message": "Usuario creado exitosamente"}), 201

@auth_bp.route('/api/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """Listar usuarios (solo admin)"""
    current_user = get_jwt_identity()
    if current_user != 'jhonny':
        return jsonify({"error": "No autorizado"}), 403
    
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id, 
        'username': u.username,
        'rol': u.rol,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in usuarios])

@auth_bp.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(user_id):
    """Eliminar usuario (solo admin)"""
    current_user = get_jwt_identity()
    if current_user != 'jhonny':
        return jsonify({"error": "No autorizado"}), 403
    
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    if usuario.username == 'jhonny':
        return jsonify({"error": "No puedes eliminar el admin principal"}), 400
    
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({"message": "Usuario eliminado"}), 200