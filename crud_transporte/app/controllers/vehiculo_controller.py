from flask import Blueprint, jsonify, request
from app.services.vehiculo_service import VehiculoService

vehiculo_bp = Blueprint('vehiculo', __name__, url_prefix='/api/vehiculos')

@vehiculo_bp.route('', methods=['GET'])
def get_vehiculos():
    """Obtener todos los vehículos"""
    try:
        # Parámetros de consulta
        tipo = request.args.get('tipo')
        estado = request.args.get('estado')
        estado_ruta = request.args.get('estado_ruta')
        with_ubicacion = request.args.get('with_ubicacion', 'false').lower() == 'true'
        solo_disponibles = request.args.get('solo_disponibles', 'false').lower() == 'true'
        
        # Obtener vehículos según filtros
        if tipo:
            vehiculos = VehiculoService.get_by_tipo(tipo, solo_disponibles, with_ubicacion)
        elif solo_disponibles:
            vehiculos = VehiculoService.get_all(with_ubicacion)
            vehiculos = [v for v in vehiculos if v.estado == 'disponible' and v.estado_ruta == 'disponible']
        else:
            vehiculos = VehiculoService.get_all(with_ubicacion)
        
        # Filtrar por estado si se especifica
        if estado:
            vehiculos = [v for v in vehiculos if v.estado == estado]
        
        # Filtrar por estado_ruta si se especifica
        if estado_ruta:
            vehiculos = [v for v in vehiculos if v.estado_ruta == estado_ruta]
        
        return jsonify([v.to_dict(include_ubicacion=with_ubicacion) for v in vehiculos])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>', methods=['GET'])
def get_vehiculo(id):
    """Obtener un vehículo por ID"""
    try:
        with_ubicacion = request.args.get('with_ubicacion', 'false').lower() == 'true'
        
        vehiculo = VehiculoService.get_by_id(id, with_ubicacion)
        if not vehiculo:
            return jsonify({'error': 'Vehículo no encontrado'}), 404
        
        return jsonify(vehiculo.to_dict(include_ubicacion=with_ubicacion))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('', methods=['POST'])
def create_vehiculo():
    """Crear un nuevo vehículo"""
    try:
        data = request.json
        
        # Validar datos requeridos
        campos_requeridos = ['tipo', 'modelo', 'codigo_serial']
        faltantes = [campo for campo in campos_requeridos if campo not in data]
        if faltantes:
            return jsonify({'error': f'Faltan campos requeridos: {", ".join(faltantes)}'}), 400
        
        # Crear vehículo usando el servicio
        vehiculo, error = VehiculoService.create(data)
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Vehículo creado exitosamente',
            'data': vehiculo.to_dict(include_ubicacion=True)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>', methods=['PUT'])
def update_vehiculo(id):
    """Actualizar un vehículo"""
    try:
        data = request.json
        
        # Actualizar usando el servicio
        vehiculo, error = VehiculoService.update(id, data)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({
            'message': 'Vehículo actualizado',
            'data': vehiculo.to_dict(include_ubicacion=True)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehiculo(id):
    """Eliminar un vehículo"""
    try:
        # Eliminar usando el servicio
        success, error = VehiculoService.delete(id)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({'message': 'Vehículo eliminado'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>/estado', methods=['PUT', 'PATCH'])
def cambiar_estado_vehiculo(id):
    """Cambiar el estado de un vehículo"""
    try:
        data = request.json
        if not data or 'estado' not in data:
            return jsonify({'error': 'Se requiere el campo "estado"'}), 400
        
        nuevo_estado = data['estado']
        
        # Cambiar estado usando el servicio
        vehiculo, error = VehiculoService.cambiar_estado(id, nuevo_estado)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({
            'success': True,
            'message': f'Estado cambiado a "{nuevo_estado}"',
            'data': vehiculo.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>/estado-ruta', methods=['PUT', 'PATCH'])
def cambiar_estado_ruta_vehiculo(id):
    """Cambiar el estado de ruta de un vehículo"""
    try:
        data = request.json
        if not data or 'estado_ruta' not in data:
            return jsonify({'error': 'Se requiere el campo "estado_ruta"'}), 400
        
        nuevo_estado_ruta = data['estado_ruta']
        
        # Cambiar estado de ruta usando el servicio
        vehiculo, error = VehiculoService.cambiar_estado_ruta(id, nuevo_estado_ruta)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({
            'success': True,
            'message': f'Estado de ruta cambiado a "{nuevo_estado_ruta}"',
            'data': vehiculo.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>/ubicacion', methods=['GET'])
def get_ubicacion_vehiculo(id):
    """Obtener la ubicación de un vehículo"""
    try:
        ubicacion, error = VehiculoService.obtener_ubicacion(id)
        if error:
            return jsonify({'error': error}), 404
        
        return jsonify(ubicacion.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>/ubicacion', methods=['PUT', 'PATCH', 'POST'])
def actualizar_ubicacion_vehiculo(id):
    """Actualizar o crear ubicación de un vehículo"""
    try:
        data = request.json
        
        # Validar campos requeridos
        if 'latitud' not in data or 'longitud' not in data:
            return jsonify({'error': 'Se requieren los campos latitud y longitud'}), 400
        
        latitud = float(data['latitud'])
        longitud = float(data['longitud'])
        direccion = data.get('direccion')
        barrio = data.get('barrio')
        ciudad = data.get('ciudad', 'Bogotá')
        
        # Actualizar ubicación usando el servicio
        success, error = VehiculoService.actualizar_ubicacion(
            id, latitud, longitud, direccion, barrio, ciudad
        )
        
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        # Obtener la ubicación actualizada para devolverla
        ubicacion, _ = VehiculoService.obtener_ubicacion(id)
        
        return jsonify({
            'success': True,
            'message': 'Ubicación actualizada',
            'data': ubicacion.to_dict() if ubicacion else None
        })
        
    except ValueError:
        return jsonify({'error': 'Latitud y longitud deben ser números válidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/buscar/cercanos', methods=['GET'])
def buscar_vehiculos_cercanos():
    """Buscar vehículos cercanos a una ubicación"""
    try:
        # Obtener parámetros
        latitud = request.args.get('latitud', type=float)
        longitud = request.args.get('longitud', type=float)
        radio_km = request.args.get('radio_km', 5.0, type=float)
        tipo = request.args.get('tipo')
        
        if latitud is None or longitud is None:
            return jsonify({'error': 'Se requieren los parámetros latitud y longitud'}), 400
        
        # Validar coordenadas
        if not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
            return jsonify({'error': 'Coordenadas fuera de rango válido'}), 400
        
        # Buscar vehículos cercanos
        vehiculos = VehiculoService.buscar_por_ubicacion(latitud, longitud, radio_km)
        
        # Filtrar por tipo si se especifica
        if tipo:
            vehiculos = [v for v in vehiculos if v.tipo == tipo]
        
        # Formatear respuesta con distancia
        resultados = []
        for vehiculo in vehiculos:
            data = vehiculo.to_dict(include_ubicacion=True)
            data['distancia_km'] = getattr(vehiculo, 'distancia_km', None)
            resultados.append(data)
        
        return jsonify({
            'total': len(resultados),
            'ubicacion_consulta': {'latitud': latitud, 'longitud': longitud},
            'radio_km': radio_km,
            'vehiculos': resultados
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/camiones/disponibles', methods=['GET'])
def get_camiones_disponibles():
    """Obtener camiones disponibles"""
    try:
        with_ubicacion = request.args.get('with_ubicacion', 'true').lower() == 'true'
        
        camiones = VehiculoService.get_camiones_disponibles(with_ubicacion)
        
        return jsonify({
            'total': len(camiones),
            'camiones': [c.to_dict(include_ubicacion=with_ubicacion) for c in camiones]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/estadisticas', methods=['GET'])
def get_estadisticas():
    """Obtener estadísticas de vehículos"""
    try:
        estadisticas = VehiculoService.get_estadisticas()
        return jsonify(estadisticas)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>/conductor', methods=['PUT', 'PATCH'])
def asignar_conductor(id):
    """Asignar conductor a un vehículo"""
    try:
        data = request.json
        if not data or 'conductor_id' not in data:
            return jsonify({'error': 'Se requiere el campo "conductor_id"'}), 400
        
        conductor_id = data['conductor_id']
        
        # Asignar conductor usando el servicio
        vehiculo, error = VehiculoService.asignar_conductor(id, conductor_id)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({
            'success': True,
            'message': f'Conductor asignado al vehículo',
            'data': vehiculo.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/<int:id>/conductor', methods=['DELETE'])
def desasignar_conductor(id):
    """Desasignar conductor de un vehículo"""
    try:
        # Desasignar conductor usando el servicio
        vehiculo, error = VehiculoService.desasignar_conductor(id)
        if error:
            return jsonify({'error': error}), 404 if 'no encontrado' in error.lower() else 400
        
        return jsonify({
            'success': True,
            'message': 'Conductor desasignado del vehículo',
            'data': vehiculo.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/tipos', methods=['GET'])
def get_tipos_vehiculos():
    """Obtener lista de tipos de vehículos disponibles"""
    try:
        # Esto debería venir de la definición del ENUM en la base de datos
        # Por ahora, lo definimos manualmente
        tipos = ['auto', 'camion']
        
        return jsonify({
            'tipos': tipos,
            'total': len(tipos)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vehiculo_bp.route('/filtrar', methods=['GET'])
def filtrar_vehiculos():
    """Filtrar vehículos con múltiples criterios"""
    try:
        # Obtener todos los parámetros de filtro
        tipo = request.args.get('tipo')
        estado = request.args.get('estado')
        estado_ruta = request.args.get('estado_ruta')
        marca = request.args.get('marca')
        color = request.args.get('color')
        barrio = request.args.get('barrio')
        ciudad = request.args.get('ciudad')
        with_ubicacion = request.args.get('with_ubicacion', 'false').lower() == 'true'
        
        # Obtener todos los vehículos (con ubicación si se solicita)
        vehiculos = VehiculoService.get_all(with_ubicacion)
        
        # Aplicar filtros
        if tipo:
            vehiculos = [v for v in vehiculos if v.tipo == tipo]
        if estado:
            vehiculos = [v for v in vehiculos if v.estado == estado]
        if estado_ruta:
            vehiculos = [v for v in vehiculos if v.estado_ruta == estado_ruta]
        if marca:
            vehiculos = [v for v in vehiculos if v.marca and v.marca.lower() == marca.lower()]
        if color:
            vehiculos = [v for v in vehiculos if v.color and v.color.lower() == color.lower()]
        
        # Filtrar por ubicación si se solicita
        if barrio and with_ubicacion:
            vehiculos = [v for v in vehiculos if v.ubicacion and v.ubicacion.barrio and 
                        v.ubicacion.barrio.lower() == barrio.lower()]
        if ciudad and with_ubicacion:
            vehiculos = [v for v in vehiculos if v.ubicacion and v.ubicacion.ciudad and 
                        v.ubicacion.ciudad.lower() == ciudad.lower()]
        
        return jsonify({
            'total': len(vehiculos),
            'filtros_aplicados': {
                'tipo': tipo,
                'estado': estado,
                'estado_ruta': estado_ruta,
                'marca': marca,
                'color': color,
                'barrio': barrio,
                'ciudad': ciudad
            },
            'vehiculos': [v.to_dict(include_ubicacion=with_ubicacion) for v in vehiculos]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500