import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración de Base de Datos
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'sistema_transporte')
    
    # Escapar contraseña si tiene caracteres especiales
    escaped_password = quote_plus(DB_PASSWORD)
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{escaped_password}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta_super_segura_123')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Swagger
    SWAGGER_URL = '/api/docs'
    SWAGGER_API_URL = '/static/swagger.json'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}