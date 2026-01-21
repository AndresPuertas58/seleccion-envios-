from flask import Blueprint, jsonify
from app.services.database_service import DatabaseService
from app.docs.estadisticas_docs import estadisticas_docs

estadisticas_bp = Blueprint('estadisticas', __name__, url_prefix='/api')

@estadisticas_bp.route('/estadisticas', methods=['GET'])
def get_estadisticas():
    """Obtener estadísticas del sistema"""
    estadisticas = DatabaseService.get_estadisticas_generales()
    if not estadisticas:
        return jsonify({'error': 'Error al obtener estadísticas'}), 500
    return jsonify(estadisticas)

@estadisticas_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado del sistema"""
    db_healthy, db_message = DatabaseService.health_check()
    
    if db_healthy:
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': '2024-01-08T00:00:00Z'
        })
    else:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': db_message
        }), 500

# Añadir documentación Swagger
get_estadisticas.__doc__ = estadisticas_docs['get_estadisticas']
health_check.__doc__ = estadisticas_docs['health_check']