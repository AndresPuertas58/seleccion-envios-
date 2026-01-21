from flask import Blueprint, jsonify, request
from app.services.envio_service import EnvioService

envio_bp = Blueprint('envio', __name__, url_prefix='/api/envios')

@envio_bp.route('', methods=['GET'])
def get_envios():
    """Obtener todos los envíos"""
    try:
        include_punto_venta = request.args.get('include_punto_venta', 'false').lower() == 'true'
        
        envios = EnvioService.get_all(include_punto_venta)
        return jsonify([envio.to_dict(include_punto_venta=include_punto_venta) for envio in envios])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@envio_bp.route('/<int:id>', methods=['GET'])
def get_envio(id):
    """Obtener un envío por ID"""
    try:
        include_punto_venta = request.args.get('include_punto_venta', 'false').lower() == 'true'
        
        envio = EnvioService.get_by_id(id, include_punto_venta)
        if not envio:
            return jsonify({'error': 'Envío no encontrado'}), 404
        
        return jsonify(envio.to_dict(include_punto_venta=include_punto_venta))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@envio_bp.route('/crear', methods=['POST'])
def create_envio():
    """Crear un nuevo envío"""
    try:
        data = request.json
        
        # Validar datos requeridos
        campos_requeridos = ['punto_venta_id', 'tipo_carga', 'peso_carga', 'remitente', 'destino']
        faltantes = [campo for campo in campos_requeridos if campo not in data]
        if faltantes:
            return jsonify({'error': f'Faltan campos requeridos: {", ".join(faltantes)}'}), 400
        
        # Crear envío
        envio, error = EnvioService.create(data)
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Envío creado exitosamente',
            'data': envio.to_dict(include_punto_venta=True)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@envio_bp.route('/punto-venta/<int:punto_venta_id>', methods=['GET'])
def get_envios_por_punto_venta(punto_venta_id):
    """Obtener envíos por punto de venta"""
    try:
        envios = EnvioService.get_by_punto_venta(punto_venta_id)
        return jsonify([envio.to_dict() for envio in envios])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@envio_bp.route('/estado/<string:estado>', methods=['GET'])
def get_envios_por_estado(estado):
    """Obtener envíos por estado"""
    try:
        envios = EnvioService.get_by_estado(estado)
        return jsonify([envio.to_dict() for envio in envios])
    except Exception as e:
        return jsonify({'error': str(e)}), 500