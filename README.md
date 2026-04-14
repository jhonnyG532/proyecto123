# 🚀 Ovni Burger - Proyectolisto para Web

## Estructura

```
proyecto123/
├── proyecto.py              # Python: python proyecto.py
├── config.py               # Configuración segurizada
├── cafeteria.db           # Base de datos SQLite
├── base_datos_segura.sql  # Schema PostgreSQL
├── README.md               # Este archivo
└── app/
    ├── __init__.py        # Aplicación Flask
    ├── models.py          # Modelos de datos
    ├── routes.py         # API con seguridad
    ├── auth.py            # Autenticación JWT segura
    ├── static/
    │   ├── css/style.css
    │   └── js/main.js
    └── templates/
        ├── base.html
        ├── index.html
        ├── admin.html
        ├── login.html
        └── sugerencias.html
```

## Iniciar Desarrollo

```bash
cd ~/Descargas/proyecto123
python proyecto.py
```

**Acceso:**
- Menú: http://192.168.0.117:5000
- Admin: http://192.168.0.117:5000/panel-galaxia-2026
- Usuario: jhonny
- Contraseña: 5331

---

## Seguridad Implementada

- ✅ Rate limiting (previene ataques de fuerza bruta)
- ✅ Sanitización de entrada (previene XSS)
- ✅ Tokens JWT seguros (1 hora de validez)
- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Sesiones HTTP-only cookies
- ✅ Rutas de admin obfuscadas
- ✅ Validación de datos
- ✅ Límite de tamaño de requests

---

## Producción (Docker)

### Opción 1: Docker Compose (Recomendado)

Crear `docker-compose.yml`:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: 5331
      POSTGRES_DB: ovni_burger
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:5331@postgres:5432/ovni_burger
    depends_on:
      - postgres

volumes:
  db_data:
```

### Opción 2: VPS/Producción Manual

```bash
# 1. Instalar dependencias
pip install flask flask-sqlalchemy flask-jwt-extended gunicorn

# 2. Configurar PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
export FLASK_ENV=production

# 3. Ejecutar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 proyecto:app
```

---

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| SECRET_KEY | Clave secreta Flask | Auto-generada |
| JWT_SECRET_KEY | Clave JWT | Auto-generada |
| DATABASE_URL | Connection string BD | SQLite local |
| FLASK_ENV | environment | development |
| CORS_ORIGINS | Origins permitidos | * |

---

## Puertos

| Servicio | Puerto |
|----------|--------|
| App (dev) | 5000 |
| PostgreSQL | 5432 |
| Nginx | 80, 443 |

---

## API Endpoints

### Públicos
- `GET /` - Menú
- `GET /sugerencias` - Página sugerencias
- `POST /api/sugerencias` - Enviar sugerencia
- `GET /api/configuracion` - Ver config
- `GET /api/categorias` - Ver categorías
- `GET /<admin_path>` - Login admin

### Protegidos (JWT required)
- `POST /api/login` - Iniciar sesión
- `POST /api/logout` - Cerrar sesión
- `GET /api/sugerencias` - Ver sugerencias
- `DELETE /api/sugerencias/<id>` - Eliminar sugerencia
- `GET/POST /api/productos` - Gestionar productos
- `GET/POST /api/categorias` - Gestionar categorías
- `GET/PUT /api/configuracion` - Gestionar configuración
- `GET /api/usuarios` - Listar usuarios
- `POST /api/registro` - Crear usuario
- `DELETE /api/usuarios/<id>` - Eliminar usuario

---

## Troubleshooting

### Error de conexión a BD
```bash
# Verificar que la DB existe
ls -la cafeteria.db

# Recrear base de datos
rm cafeteria.db
python proyecto.py
```

### Docker no funciona
```bash
# Instalar Docker
sudo dnf install docker

# Iniciar servicio
sudo systemctl start docker

# Ejecutar compose
sudo docker-compose up -d
```

---

## Licencia
© 2026 Ovni Burger