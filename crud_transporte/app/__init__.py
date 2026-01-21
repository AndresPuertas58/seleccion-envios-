from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from config import config
import os

# Inicializar extensiones
db = SQLAlchemy()
cors = CORS()

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configurar aplicación
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    cors.init_app(app)
    
    # Configurar Swagger UI
    SWAGGER_URL = app.config.get('SWAGGER_URL', '/api/docs')
    API_URL = app.config.get('SWAGGER_API_URL', '/static/swagger.yaml')
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "API Sistema de Transporte"}
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Importar y registrar blueprints
    from app.controllers.vehiculo_controller import vehiculo_bp
    from app.controllers.conductor_controller import conductor_bp
    from app.controllers.usuario_controller import usuario_bp
    from app.controllers.estadisticas_controller import estadisticas_bp
    from app.controllers.punto_venta_controller import punto_venta_bp
    from app.controllers.envio_controller import envio_bp
    from app.controllers.asignacion_controller import asignacion_bp


    app.register_blueprint(asignacion_bp)
    app.register_blueprint(punto_venta_bp)
    app.register_blueprint(envio_bp)
    app.register_blueprint(vehiculo_bp)
    app.register_blueprint(conductor_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(estadisticas_bp)
    
    # Ruta raíz
    @app.route('/')
    def index():
        return jsonify({
            'message': 'API Sistema de Transporte',
            'version': '1.0',
            'documentation': f'{SWAGGER_URL}',
            'endpoints': {
                'vehiculos': '/api/vehiculos',
                'conductores': '/api/conductores',
                'usuarios': '/api/usuarios',
                'estadisticas': '/api/estadisticas',
                'health': '/api/health'
            }
        })
    
    # Crear carpeta static si no existe
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Generar documentación Swagger
    from app.docs.swagger_config import save_swagger_yaml
    save_swagger_yaml()
    
    return app