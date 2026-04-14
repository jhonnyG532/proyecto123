import os
import secrets

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEFAULT_INSTAGRAM_HANDLE = os.environ.get('INSTAGRAM_HANDLE', 'burger.ovni')
    
    # Seguridad: Claves secretas seguras
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(64)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(64)
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'sqlite:///' + os.path.join(BASE_DIR, 'cafeteria.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Seguridad JWT
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    
    # Seguridad de cookies
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Seguridad extra
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False
    
    # Límites de tamaño
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # CORS (para producción)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


# Rate limiting simple (en memoria)
class RateLimiter:
    def __init__(self):
        self.attempts = {}
        self.max_attempts = 5
        self.window_seconds = 300  # 5 minutos
    
    def check(self, key):
        import time
        now = time.time()
        if key in self.attempts:
            count, first_attempt = self.attempts[key]
            if now - first_attempt < self.window_seconds:
                if count >= self.max_attempts:
                    return False
                self.attempts[key] = (count + 1, first_attempt)
            else:
                self.attempts[key] = (1, now)
        else:
            self.attempts[key] = (1, now)
        return True
    
    def reset(self, key):
        if key in self.attempts:
            del self.attempts[key]


rate_limiter = RateLimiter()