from flask import Blueprint, jsonify, request
from app.services.punto_venta_service import PuntoVentaService

punto_venta_bp = Blueprint('punto_venta', __name__, url_prefix='/api/puntos-venta')

@punto_venta_bp.route('', methods=['GET'])
def get_puntos_venta():
    """Obtener todos los puntos de venta"""
    try:
        puntos = PuntoVentaService.get_all()
        return jsonify([punto.to_dict() for punto in puntos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@punto_venta_bp.route('/<int:id>', methods=['GET'])
def get_punto_venta(id):
    """Obtener un punto de venta por ID"""
    try:
        punto = PuntoVentaService.get_by_id(id)
        if not punto:
            return jsonify({'error': 'Punto de venta no encontrado'}), 404
        
        return jsonify(punto.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@punto_venta_bp.route('/crear', methods=['POST'])
def create_punto_venta():
    """Crear un nuevo punto de venta"""
    try:
        data = request.json
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'latitud', 'longitud']
        faltantes = [campo for campo in campos_requeridos if campo not in data]
        if faltantes:
            return jsonify({'error': f'Faltan campos requeridos: {", ".join(faltantes)}'}), 400
        
        # Crear punto de venta
        punto_venta, error = PuntoVentaService.create(data)
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Punto de venta creado exitosamente',
            'data': punto_venta.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@punto_venta_bp.route('/activos', methods=['GET'])
def get_puntos_venta_activos():
    """Obtener puntos de venta activos"""
    try:
        puntos = PuntoVentaService.get_active()
        return jsonify([punto.to_dict() for punto in puntos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@punto_venta_bp.route('/cercanos', methods=['GET'])
def get_puntos_venta_cercanos():
    """Obtener puntos de venta cercanos a una ubicación"""
    try:
        latitud = request.args.get('latitud', type=float)
        longitud = request.args.get('longitud', type=float)
        radio_km = request.args.get('radio_km', 5.0, type=float)
        
        if latitud is None or longitud is None:
            return jsonify({'error': 'Se requieren latitud y longitud'}), 400
        
        puntos = PuntoVentaService.get_nearby(latitud, longitud, radio_km)
        
        resultados = []
        for punto in puntos:
            data = punto.to_dict()
            data['distancia_km'] = getattr(punto, 'distancia_km', None)
            resultados.append(data)
        
        return jsonify({
            'total': len(resultados),
            'ubicacion_consulta': {'latitud': latitud, 'longitud': longitud},
            'radio_km': radio_km,
            'puntos_venta': resultados
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500