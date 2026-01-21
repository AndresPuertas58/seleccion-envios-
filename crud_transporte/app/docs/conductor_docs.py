# Documentación similar para conductores
conductor_docs = {
    'get_conductores': 'Obtener todos los conductores',
    'get_conductor': 'Obtener un conductor por ID',
    'create_conductor': 'Crear un nuevo conductor',
    'update_conductor': 'Actualizar un conductor existente',
    'delete_conductor': 'Eliminar un conductor'
}

conductor_swagger = {
    '/api/conductores': {
        'get': {
            'tags': ['Conductores'],
            'summary': 'Obtener todos los conductores',
            'responses': {
                '200': {
                    'description': 'Lista de conductores',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {'$ref': '#/components/schemas/Conductor'}
                            }
                        }
                    }
                }
            }
        },
        'post': {
            'tags': ['Conductores'],
            'summary': 'Crear un nuevo conductor',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['dni', 'nombre', 'apellido'],
                            'properties': {
                                'dni': {'type': 'string', 'example': '12345678'},
                                'nombre': {'type': 'string', 'example': 'Juan'},
                                'apellido': {'type': 'string', 'example': 'Pérez'},
                                'licencia': {'type': 'string', 'example': 'A1'},
                                'telefono': {'type': 'string', 'example': '555-1234'},
                                'email': {'type': 'string', 'format': 'email', 'example': 'juan@example.com'},
                                'direccion': {'type': 'string', 'example': 'Calle Principal 123'},
                                'fecha_nacimiento': {'type': 'string', 'format': 'date', 'example': '1980-05-15'},
                                'estado': {'type': 'string', 'example': 'activo'}
                            }
                        }
                    }
                }
            },
            'responses': {
                '201': {
                    'description': 'Conductor creado exitosamente',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Conductor'}
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
    '/api/conductores/{id}': {
        'get': {
            'tags': ['Conductores'],
            'summary': 'Obtener un conductor por ID',
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
                    'description': 'Datos del conductor',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Conductor'}
                        }
                    }
                },
                '404': {'$ref': '#/components/responses/404'}
            }
        },
        'put': {
            'tags': ['Conductores'],
            'summary': 'Actualizar un conductor',
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
                    'description': 'Conductor actualizado',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Conductor'}
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
            'tags': ['Conductores'],
            'summary': 'Eliminar un conductor',
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
                    'description': 'Conductor eliminado',
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