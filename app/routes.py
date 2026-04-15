import os
import uuid
from flask import Blueprint, render_template, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
main_bp = Blueprint('main', __name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Rate limiting global
api_rate_limit = {}

def sanitize_html(text):
    """Sanitizar HTML para prevenir XSS"""
    if not text:
        return ''
    # Eliminar etiquetas HTML peligrosas
    dangerous = ['<script', 'javascript:', 'onerror=', 'onclick=', 'onload=']
    result = text
    for d in dangerous:
        result = result.replace(d, '')
    return result

def get_client_ip():
    """Obtener IP real del cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def check_api_rate(ip, endpoint, limit=30, window=60):
    """Rate limiting por endpoint"""
    key = f"{ip}:{endpoint}"
    now = time.time()
    if key in api_rate_limit:
        count, start = api_rate_limit[key]
        if now - start < window:
            if count >= limit:
                return False
            api_rate_limit[key] = (count + 1, start)
        else:
            api_rate_limit[key] = (1, now)
    else:
        api_rate_limit[key] = (1, now)
    return True

# Funciones helper
def whatsapp_digits_from_telefono(telefono):
    if not telefono: return ''
    digits = ''.join(c for c in telefono if c.isdigit())
    if len(digits) == 10 and not digits.startswith('57'):
        digits = '57' + digits
    return digits

def instagram_url_from_handle(handle):
    h = (handle or '').strip().lstrip('@').rstrip('/')
    if not h: return ''
    return f'https://www.instagram.com/{h}/'

def whatsapp_chat_url(digits):
    if not digits: return ''
    return f'https://wa.me/{digits}'

# Ruta secreta para admin
SECRET_ADMIN_PATH = 'panel-galaxia-2026'

# ============= RUTAS PÚBLICAS =============

@main_bp.route('/')
def index():
    """Página principal - menú"""
    productos = Producto.query.filter_by(disponible=True).all()
    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.orden).all()
    configuracion = Configuracion.query.first() or Configuracion()
    wa = whatsapp_digits_from_telefono(configuracion.telefono or '')
    wa_open = whatsapp_chat_url(wa)
    ig = instagram_url_from_handle(configuracion.instagram or '')
    return render_template('index.html', 
        productos=productos, config=configuracion, categorias=categorias,
        whatsapp_digits=wa, whatsapp_url_open=wa_open, instagram_url=ig)

@main_bp.route('/sugerencias')
def sugerencias():
    """Página de sugerencias"""
    configuracion = Configuracion.query.first() or Configuracion()
    wa = whatsapp_digits_from_telefono(configuracion.telefono or '')
    wa_open = whatsapp_chat_url(wa)
    ig = instagram_url_from_handle(configuracion.instagram or '')
    return render_template('sugerencias.html', 
        whatsapp_digits=wa, whatsapp_url_open=wa_open, instagram_url=ig)

@main_bp.route('/' + SECRET_ADMIN_PATH)
def admin():
    """Login de admin"""
    return render_template('login.html')

@main_bp.route('/' + SECRET_ADMIN_PATH + '/dashboard')
def admin_dashboard():
    """Panel de admin"""
    return render_template('admin.html')

# ============= API SUGERENCIAS =============

@main_bp.route('/api/sugerencias', methods=['POST'])
def enviar_sugerencia():
    """Enviar sugerencia (público)"""
    ip = get_client_ip()
    if not check_api_rate(ip, 'sugerencias', limit=10, window=60):
        return jsonify({"error": "Demasiadas solicitudes"}), 429
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    mensaje = data.get('mensaje', '')
    if not mensaje or len(mensaje) < 3:
        return jsonify({"error": "Mensaje requerido"}), 400
    
    # Sanitizar mensaje
    mensaje = sanitize_html(mensaje[:500])  # Limitar a 500 caracteres
    
    sugerencia = Sugerencia(
        nombre=sanitize_html(data.get('nombre', 'Anónimo')[:100]),
        telefono=sanitize_html(data.get('telefono', '')[:20]),
        correo=sanitize_html(data.get('correo', '')[:100]),
        tipo=data.get('tipo', 'sugerencia'),
        mensaje=mensaje,
        rating=min(max(data.get('rating', 5), 1), 5)
    )
    db.session.add(sugerencia)
    db.session.commit()
    return jsonify({
        "message": "¡Gracias! Tu opinión es importante.",
        "id": sugerencia.id
    }), 201

@main_bp.route('/api/sugerencias', methods=['GET'])
@jwt_required()
def get_sugerencias():
    """Obtener sugerencias (admin)"""
    sugerencias = Sugerencia.query.order_by(Sugerencia.created_at.desc()).all()
    return jsonify([{
        'id': s.id, 
        'nombre': s.nombre, 
        'telefono': s.telefono, 
        'correo': s.correo,
        'tipo': s.tipo, 
        'mensaje': s.mensaje, 
        'rating': s.rating,
        'created_at': s.created_at.isoformat() if s.created_at else None
    } for s in sugerencias])

@main_bp.route('/api/sugerencias/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_sugerencia(id):
    """Eliminar sugerencia (admin)"""
    sugerencia = Sugerencia.query.get_or_404(id)
    db.session.delete(sugerencia)
    db.session.commit()
    return jsonify({"message": "Sugerencia eliminada"}), 200

# ============= API PRODUCTOS =============

@main_bp.route('/api/productos', methods=['GET', 'POST'])
@jwt_required()
def get_productos():
    """Gestionar productos (admin)"""
    if request.method == 'POST':
        ip = get_client_ip()
        if not check_api_rate(ip, 'productos', limit=10, window=60):
            return jsonify({"error": "Demasiadas solicitudes"}), 429
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Datos inválidos"}), 400
        
        # Validar datos
        nombre = sanitize_html(data.get('nombre', ''))
        if not nombre or len(nombre) < 2:
            return jsonify({"error": "Nombre requerido"}), 400
        
        producto = Producto(
            codigo=sanitize_html(data.get('codigo', '')),
            nombre=nombre[:100],
            descripcion=sanitize_html(data.get('descripcion', ''))[:500],
            precio=max(data.get('precio', 0), 0),
            categoria=sanitize_html(data.get('categoria', ''))[:50],
            imagen=sanitize_html(data.get('imagen', ''))[:300],
            stock=max(data.get('stock', 100), 0),
            disponible=data.get('disponible', True)
        )
        db.session.add(producto)
        db.session.commit()
        return jsonify({"message": "Producto creado"}), 201
    
    productos = Producto.query.all()
    return jsonify([{
        'id': p.id, 
        'codigo': p.codigo, 
        'nombre': p.nombre, 
        'descripcion': p.descripcion,
        'precio': p.precio, 
        'categoria': p.categoria, 
        'imagen': p.imagen,
        'stock': p.stock, 
        'disponible': p.disponible
    } for p in productos])

@main_bp.route('/api/productos/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def producto_detalle(id):
    """Gestionar producto individual (admin)"""
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'DELETE':
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"message": "Producto eliminado"})
    
    if request.method in ['PUT', 'PATCH']:
        data = request.get_json(silent=True)
        if data:
            for key in ['codigo', 'nombre', 'descripcion', 'precio', 'categoria', 'imagen', 'stock', 'disponible']:
                if key in data:
                    setattr(producto, key, data[key])
            db.session.commit()
        return jsonify({"message": "Producto actualizado"})
    
    return jsonify({
        'id': producto.id, 
        'codigo': producto.codigo, 
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'precio': producto.precio,
        'categoria': producto.categoria,
        'imagen': producto.imagen,
        'stock': producto.stock,
        'disponible': producto.disponible
    })

# ============= API CONFIGURACIÓN =============

@main_bp.route('/api/configuracion', methods=['GET'])
def get_config():
    """Obtener configuración (público)"""
    cfg = Configuracion.query.first() or Configuracion()
    return jsonify({
        'nombre_negocio': cfg.nombre_negocio,
        'direccion': cfg.direccion,
        'telefono': cfg.telefono,
        'nit': cfg.nit,
        'instagram': cfg.instagram,
        'mensaje_pie': cfg.mensaje_pie
    })

@main_bp.route('/api/configuracion', methods=['PUT'])
@jwt_required()
def update_config():
    """Actualizar configuración (admin)"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    cfg = Configuracion.query.first()
    if cfg:
        for key in ['nombre_negocio', 'direccion', 'telefono', 'nit', 'instagram', 'mensaje_pie']:
            if key in data:
                value = sanitize_html(str(data[key]))[:200]
                setattr(cfg, key, value)
    else:
        cfg = Configuracion(
            nombre_negocio=sanitize_html(data.get('nombre_negocio', 'Ovni Burger')),
            direccion=sanitize_html(data.get('direccion', '')),
            telefono=sanitize_html(data.get('telefono', '')),
            nit=sanitize_html(data.get('nit', '')),
            instagram=sanitize_html(data.get('instagram', '')),
            mensaje_pie=sanitize_html(data.get('mensaje_pie', '')))
        db.session.add(cfg)
    db.session.commit()
    return jsonify({"message": "Configuración guardada"})

# ============= API CATEGORÍAS =============

@main_bp.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Obtener categorías"""
    include_inactive = request.args.get('all') == '1'
    query = Categoria.query
    if not include_inactive:
        query = query.filter_by(activa=True)
    categorias = query.order_by(Categoria.orden).all()
    return jsonify([{'id': c.id, 'nombre': c.nombre, 'icono': c.icono, 'orden': c.orden, 'activa': c.activa} for c in categorias])

@main_bp.route('/api/categorias', methods=['POST'])
@jwt_required()
def create_categoria():
    """Crear categoría (admin)"""
    data = request.get_json(silent=True)
    if not data or not data.get('nombre'):
        return jsonify({"error": "Nombre requerido"}), 400
    
    categoria = Categoria(
        nombre=sanitize_html(data.get('nombre'))[:50],
        icono=sanitize_html(data.get('icono', 'bi-folder'))[:50],
        orden=data.get('orden', 0)
    )
    db.session.add(categoria)
    db.session.commit()
    return jsonify({"message": "Categoría creada"}), 201

@main_bp.route('/api/categorias/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def update_categoria(id):
    """Gestionar categoría (admin)"""
    categoria = Categoria.query.get_or_404(id)
    
    if request.method == 'DELETE':
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({"message": "Categoría eliminada"})
    
    if request.method in ['GET']:
        return jsonify({
            'id': categoria.id,
            'nombre': categoria.nombre,
            'icono': categoria.icono,
            'orden': categoria.orden,
            'activa': categoria.activa
        })
    
    data = request.get_json(silent=True)
    if data:
        if 'nombre' in data:
            categoria.nombre = sanitize_html(data['nombre'][:50])
        if 'icono' in data:
            categoria.icono = sanitize_html(data['icono'][:50])
        if 'orden' in data:
            categoria.orden = data['orden']
        if 'activa' in data:
            categoria.activa = data['activa']
        db.session.commit()
    return jsonify({"message": "Categoría actualizada"})

# ============= API IMÁGENES =============

@main_bp.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """Subir imagen al servidor"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        url = f"/static/uploads/{filename}"
        return jsonify({"url": url, "filename": filename}), 201
    
    return jsonify({"error": "File type not allowed"}), 400

@main_bp.route('/api/images', methods=['GET'])
@jwt_required()
def list_images():
    """Listar imágenes cargadas"""
    if not os.path.exists(UPLOAD_FOLDER):
        return jsonify([])
    
    images = []
    for f in os.listdir(UPLOAD_FOLDER):
        if allowed_file(f):
            images.append({
                "name": f,
                "url": f"/static/uploads/{f}"
            })
    return jsonify(images)

@main_bp.route('/api/images/<name>', methods=['DELETE'])
@jwt_required()
def delete_image(name):
    """Eliminar imagen"""
    filepath = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "Imagen eliminada"})
    return jsonify({"error": "Imagen no encontrada"}), 404