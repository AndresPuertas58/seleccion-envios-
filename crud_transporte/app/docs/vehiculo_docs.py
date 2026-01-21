# Documentación Swagger para endpoints de vehículos
vehiculo_docs = {
    'get_vehiculos': """
    Obtener todos los vehículos registrados en el sistema.
    
    Returns:
        List[Vehiculo]: Lista de vehículos
    """,
    
    'get_vehiculo': """
    Obtener un vehículo específico por su ID.
    
    Parameters:
        id (int): ID del vehículo
    
    Returns:
        Vehiculo: Datos del vehículo
    """,
    
    'create_vehiculo': """
    Crear un nuevo vehículo en el sistema.
    
    Body:
        tipo (str): Tipo de vehículo (requerido)
        modelo (str): Modelo del vehículo (requerido)
        codigo_serial (str): Código serial único (requerido)
        marca (str): Marca del vehículo
        placa (str): Placa del vehículo
        color (str): Color del vehículo
        estado (str): Estado del vehículo (default: disponible)
        fecha_adquisicion (str): Fecha de adquisición (YYYY-MM-DD)
        ultimo_mantenimiento (str): Fecha del último mantenimiento (YYYY-MM-DD)
    
    Returns:
        dict: Vehículo creado y mensaje de éxito
    """,
    
    'update_vehiculo': """
    Actualizar los datos de un vehículo existente.
    
    Parameters:
        id (int): ID del vehículo a actualizar
    
    Returns:
        dict: Vehículo actualizado y mensaje de éxito
    """,
    
    'delete_vehiculo': """
    Eliminar un vehículo del sistema.
    
    Parameters:
        id (int): ID del vehículo a eliminar
    
    Returns:
        dict: Mensaje de confirmación
    """
}

# Definiciones Swagger para vehículos
vehiculo_swagger = {
    '/api/vehiculos': {
        'get': {
            'tags': ['Vehículos'],
            'summary': 'Obtener todos los vehículos',
            'responses': {
                '200': {
                    'description': 'Lista de vehículos',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {'$ref': '#/components/schemas/Vehiculo'}
                            }
                        }
                    }
                }
            }
        },
        'post': {
            'tags': ['Vehículos'],
            'summary': 'Crear un nuevo vehículo',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['tipo', 'modelo', 'codigo_serial'],
                            'properties': {
                                'tipo': {'type': 'string', 'example': 'Camión'},
                                'modelo': {'type': 'string', 'example': '2023'},
                                'codigo_serial': {'type': 'string', 'example': 'CT-001'},
                                'marca': {'type': 'string', 'example': 'Volvo'},
                                'placa': {'type': 'string', 'example': 'ABC-123'},
                                'color': {'type': 'string', 'example': 'Rojo'},
                                'estado': {'type': 'string', 'example': 'disponible'},
                                'fecha_adquisicion': {'type': 'string', 'format': 'date', 'example': '2023-01-15'},
                                'ultimo_mantenimiento': {'type': 'string', 'format': 'date', 'example': '2023-12-01'}
                            }
                        }
                    }
                }
            },
            'responses': {
                '201': {
                    'description': 'Vehículo creado exitosamente',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Vehiculo'}
                                }
                            }
                        }
                    }
                },
                '400': {'$ref': '#/components/responses/400'},
                '500': {'$ref': '#/components/responses/500'}
            }
        }
    },
    '/api/vehiculos/{id}': {
        'get': {
            'tags': ['Vehículos'],
            'summary': 'Obtener un vehículo por ID',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'integer'},
                    'description': 'ID del vehículo'
                }
            ],
            'responses': {
                '200': {
                    'description': 'Datos del vehículo',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Vehiculo'}
                        }
                    }
                },
                '404': {'$ref': '#/components/responses/404'}
            }
        },
        'put': {
            'tags': ['Vehículos'],
            'summary': 'Actualizar un vehículo',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'integer'}
                }
            ],
            'responses': {
                '200': {
                    'description': 'Vehículo actualizado',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Vehiculo'}
                                }
                            }
                        }
                    }
                },
                '404': {'$ref': '#/components/responses/404'},
                '500': {'$ref': '#/components/responses/500'}
            }
        },
        'delete': {
            'tags': ['Vehículos'],
            'summary': 'Eliminar un vehículo',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'integer'}
                }
            ],
            'responses': {
                '200': {
                    'description': 'Vehículo eliminado',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Success'}
                        }
                    }
                },
                '404': {'$ref': '#/components/responses/404'},
                '500': {'$ref': '#/components/responses/500'}
            }
        }
    }
}