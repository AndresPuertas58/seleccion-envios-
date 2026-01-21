from flask import Blueprint, jsonify, request
from app.services.usuario_service import UsuarioService
from app.docs.usuario_docs import usuario_docs

usuario_bp = Blueprint('usuario', __name__, url_prefix='/api/usuarios')

@usuario_bp.route('', methods=['GET'])
def get_usuarios():
    """Obtener todos los usuarios"""
    usuarios = UsuarioService.get_all()
    return jsonify([u.to_dict() for u in usuarios])

@usuario_bp.route('/<int:id>', methods=['GET'])
def get_usuario(id):
    """Obtener un usuario por ID"""
    usuario = UsuarioService.get_by_id(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())

@usuario_bp.route('', methods=['POST'])
def create_usuario():
    """Crear un nuevo usuario"""
    data = request.json
    
    if not data.get('username') or not data.get('email') or not data.get('nombre') or not data.get('password'):
        return jsonify({'error': 'Faltan campos requeridos: username, email, nombre, password'}), 400
    
    usuario, error = UsuarioService.create(data)
    if error:
        if "ya existe" in error.lower():
            return jsonify({'error': error}), 400
        return jsonify({'error': error}), 500
    
    return jsonify({
        'message': 'Usuario creado exitosamente',
        'data': usuario.to_dict()
    }), 201

@usuario_bp.route('/<int:id>', methods=['PUT'])
def update_usuario(id):
    """Actualizar un usuario"""
    usuario, error = UsuarioService.update(id, request.json)
    if error:
        if "no encontrado" in error.lower():
            return jsonify({'error': error}), 404
        if "ya existe" in error.lower():
            return jsonify({'error': error}), 400
        return jsonify({'error': error}), 500
    
    return jsonify({
        'message': 'Usuario actualizado',
        'data': usuario.to_dict()
    })

@usuario_bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    """Eliminar un usuario"""
    success, error = UsuarioService.delete(id)
    if error:
        if "no encontrado" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 500
    
    return jsonify({'message': 'Usuario eliminado'})

@usuario_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuario"""
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Se requiere username y password'}), 400
    
    usuario, error = UsuarioService.authenticate(data['username'], data['password'])
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({
        'message': 'Login exitoso',
        'data': usuario.to_dict()
    })

@usuario_bp.route('/<int:id>/cambiar-password', methods=['PUT'])
def cambiar_password(id):
    """Cambiar contraseña de usuario"""
    data = request.json
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Se requieren ambas contraseñas'}), 400
    
    success, error = UsuarioService.cambiar_password(id, data['current_password'], data['new_password'])
    if error:
        if "incorrecta" in error.lower():
            return jsonify({'error': error}), 401
        if "no encontrado" in error.lower():
            return jsonify({'error': error}), 404
        return jsonify({'error': error}), 500
    
    return jsonify({'message': 'Contraseña actualizada exitosamente'})

# Añadir documentación Swagger
get_usuarios.__doc__ = usuario_docs['get_usuarios']
get_usuario.__doc__ = usuario_docs['get_usuario']
create_usuario.__doc__ = usuario_docs['create_usuario']
update_usuario.__doc__ = usuario_docs['update_usuario']
delete_usuario.__doc__ = usuario_docs['delete_usuario']
login.__doc__ = usuario_docs['login']
cambiar_password.__doc__ = usuario_docs['cambiar_password']