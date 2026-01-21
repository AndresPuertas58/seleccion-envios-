from flask import Blueprint, jsonify, request
from app.services.conductor_service import ConductorService
from app.docs.conductor_docs import conductor_docs

conductor_bp = Blueprint('conductor', __name__, url_prefix='/api/conductores')

@conductor_bp.route('', methods=['GET'])
def get_conductores():
    """Obtener todos los conductores"""
    conductores = ConductorService.get_all()
    return jsonify([c.to_dict() for c in conductores])

@conductor_bp.route('/<int:id>', methods=['GET'])
def get_conductor(id):
    """Obtener un conductor por ID"""
    conductor = ConductorService.get_by_id(id)
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    return jsonify(conductor.to_dict())

@conductor_bp.route('', methods=['POST'])
def create_conductor():
    """Crear un nuevo conductor"""
    data = request.json
    
    if not data.get('dni') or not data.get('nombre') or not data.get('apellido'):
        return jsonify({'error': 'Faltan campos requeridos: dni, nombre, apellido'}), 400
    
    conductor, error = ConductorService.create(data)
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'message': 'Conductor creado exitosamente',
        'data': conductor.to_dict()
    }), 201

@conductor_bp.route('/<int:id>', methods=['PUT'])
def update_conductor(id):
    """Actualizar un conductor"""
    conductor, error = ConductorService.update(id, request.json)
    if error:
        if "no encontrado" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 500
    
    return jsonify({
        'message': 'Conductor actualizado',
        'data': conductor.to_dict()
    })

@conductor_bp.route('/<int:id>', methods=['DELETE'])
def delete_conductor(id):
    """Eliminar un conductor"""
    success, error = ConductorService.delete(id)
    if error:
        if "no encontrado" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 500
    
    return jsonify({'message': 'Conductor eliminado'})

# Añadir documentación Swagger
get_conductores.__doc__ = conductor_docs['get_conductores']
get_conductor.__doc__ = conductor_docs['get_conductor']
create_conductor.__doc__ = conductor_docs['create_conductor']
update_conductor.__doc__ = conductor_docs['update_conductor']
delete_conductor.__doc__ = conductor_docs['delete_conductor']