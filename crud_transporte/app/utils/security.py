import secrets
from datetime import datetime, timedelta
import jwt

def generate_token(user_id, secret_key, expires_in=3600):
    """Generar token JWT"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token, secret_key):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_api_key():
    """Generar clave API aleatoria"""
    return secrets.token_hex(32)