from flask import Blueprint, jsonify, request
from app.services.asignacion_service import AsignacionService
from app.models.vehiculo import Vehiculo
from app.models.conductor import Conductor

asignacion_bp = Blueprint('asignacion', __name__, url_prefix='/api/asignaciones')

@asignacion_bp.route('/asignar', methods=['POST'])
def asignar_conductor_vehiculo():
    """Asignar un conductor a un vehículo"""
    try:
        data = request.json
        
        # Validar campos requeridos
        if 'vehiculo_id' not in data or 'conductor_id' not in data:
            return jsonify({'error': 'Se requieren vehiculo_id y conductor_id'}), 400
        
        vehiculo_id = data['vehiculo_id']
        conductor_id = data['conductor_id']
        
        # Asignar conductor al vehículo
        vehiculo, error = AsignacionService.asignar_conductor_vehiculo(vehiculo_id, conductor_id)
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'message': 'Conductor asignado exitosamente al vehículo',
            'data': vehiculo.to_dict(include_conductor=True)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@asignacion_bp.route('/desasignar/<int:vehiculo_id>', methods=['POST', 'DELETE'])
def desasignar_conductor_vehiculo(vehiculo_id):
    """Desasignar conductor de un vehículo"""
    try:
        vehiculo, error = AsignacionService.desasignar_conductor_vehiculo(vehiculo_id)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({
            'success': True,
            'message': 'Conductor desasignado exitosamente',
            'data': vehiculo.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@asignacion_bp.route('/vehiculos-con-conductor', methods=['GET'])
def get_vehiculos_con_conductor():
    """Obtener vehículos con conductor asignado"""
    try:
        vehiculos = AsignacionService.get_vehiculos_con_conductor()
        
        return jsonify({
            'total': len(vehiculos),
            'vehiculos': [vehiculo.to_dict(include_conductor=True) for vehiculo in vehiculos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@asignacion_bp.route('/vehiculos-sin-conductor', methods=['GET'])
def get_vehiculos_sin_conductor():
    """Obtener vehículos sin conductor asignado"""
    try:
        vehiculos = AsignacionService.get_vehiculos_sin_conductor()
        
        return jsonify({
            'total': len(vehiculos),
            'vehiculos': [vehiculo.to_dict() for vehiculo in vehiculos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@asignacion_bp.route('/conductores-disponibles', methods=['GET'])
def get_conductores_disponibles():
    """Obtener conductores disponibles para asignar"""
    try:
        conductores = AsignacionService.get_conductores_disponibles()
        
        return jsonify({
            'total': len(conductores),
            'conductores': [conductor.to_dict() for conductor in conductores]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@asignacion_bp.route('/validar-asignacion', methods=['POST'])
def validar_asignacion():
    """Validar si se puede realizar una asignación"""
    try:
        data = request.json
        
        if 'vehiculo_id' not in data or 'conductor_id' not in data:
            return jsonify({'error': 'Se requieren vehiculo_id y conductor_id'}), 400
        
        vehiculo_id = data['vehiculo_id']
        conductor_id = data['conductor_id']
        
        # Verificar que ambos existen
        vehiculo = Vehiculo.query.get(vehiculo_id)
        conductor = Conductor.query.get(conductor_id)
        
        if not vehiculo:
            return jsonify({'error': 'Vehículo no encontrado'}), 404
        
        if not conductor:
            return jsonify({'error': 'Conductor no encontrado'}), 404
        
        # Verificar disponibilidad
        validaciones = []
        
        # Verificar conductor
        if conductor.estado != 'activo':
            validaciones.append(f"Conductor no activo (estado: {conductor.estado})")
        
        if conductor.vehiculo:
            validaciones.append(f"Conductor ya tiene vehículo asignado")
        
        # Verificar vehículo
        if vehiculo.estado != 'disponible':
            validaciones.append(f"Vehículo no disponible (estado: {vehiculo.estado})")
        
        if vehiculo.conductor:
            validaciones.append(f"Vehículo ya tiene conductor asignado")
        
        return jsonify({
            'puede_asignar': len(validaciones) == 0,
            'validaciones': validaciones,
            'vehiculo': vehiculo.to_dict(),
            'conductor': conductor.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500