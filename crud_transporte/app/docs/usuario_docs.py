# Documentación para usuarios
usuario_docs = {
    'get_usuarios': 'Obtener todos los usuarios',
    'get_usuario': 'Obtener un usuario por ID',
    'create_usuario': 'Crear un nuevo usuario',
    'update_usuario': 'Actualizar un usuario existente',
    'delete_usuario': 'Eliminar un usuario',
    'login': 'Autenticar usuario',
    'cambiar_password': 'Cambiar contraseña de usuario'
}

usuario_swagger = {
    '/api/usuarios': {
        'get': {
            'tags': ['Usuarios'],
            'summary': 'Obtener todos los usuarios',
            'responses': {
                '200': {
                    'description': 'Lista de usuarios',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {'$ref': '#/components/schemas/Usuario'}
                            }
                        }
                    }
                }
            }
        },
        'post': {
            'tags': ['Usuarios'],
            'summary': 'Crear un nuevo usuario',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['username', 'email', 'nombre', 'password'],
                            'properties': {
                                'username': {'type': 'string', 'example': 'jperez'},
                                'email': {'type': 'string', 'format': 'email', 'example': 'juan@example.com'},
                                'nombre': {'type': 'string', 'example': 'Juan Pérez'},
                                'password': {'type': 'string', 'format': 'password', 'example': 'MiClave123'},
                                'telefono': {'type': 'string', 'example': '555-1234'},
                                'activo': {'type': 'boolean', 'example': True}
                            }
                        }
                    }
                }
            },
            'responses': {
                '201': {
                    'description': 'Usuario creado exitosamente',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Usuario'}
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
    '/api/usuarios/{id}': {
        'get': {
            'tags': ['Usuarios'],
            'summary': 'Obtener un usuario por ID',
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
                    'description': 'Datos del usuario',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Usuario'}
                        }
                    }
                },
                '404': {'$ref': '#/components/responses/404'}
            }
        },
        'put': {
            'tags': ['Usuarios'],
            'summary': 'Actualizar un usuario',
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
                    'description': 'Usuario actualizado',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Usuario'}
                                }
                            }
                        }
                    }
                },
                '400': {'$ref': '#/components/responses/400'},
                '404': {'$ref': '#/components/responses/404'},
                '500': {'$ref': '#/components/responses/500'}
            }
        },
        'delete': {
            'tags': ['Usuarios'],
            'summary': 'Eliminar un usuario',
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
                    'description': 'Usuario eliminado',
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
    },
    '/api/usuarios/login': {
        'post': {
            'tags': ['Usuarios'],
            'summary': 'Autenticar usuario',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['username', 'password'],
                            'properties': {
                                'username': {'type': 'string', 'example': 'jperez'},
                                'password': {'type': 'string', 'format': 'password', 'example': 'MiClave123'}
                            }
                        }
                    }
                }
            },
            'responses': {
                '200': {
                    'description': 'Login exitoso',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string'},
                                    'data': {'$ref': '#/components/schemas/Usuario'}
                                }
                            }
                        }
                    }
                },
                '401': {'$ref': '#/components/responses/401'}
            }
        }
    },
    '/api/usuarios/{id}/cambiar-password': {
        'put': {
            'tags': ['Usuarios'],
            'summary': 'Cambiar contraseña',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'integer'}
                }
            ],
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['current_password', 'new_password'],
                            'properties': {
                                'current_password': {'type': 'string', 'format': 'password'},
                                'new_password': {'type': 'string', 'format': 'password'}
                            }
                        }
                    }
                }
            },
            'responses': {
                '200': {
                    'description': 'Contraseña actualizada',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Success'}
                        }
                    }
                },
                '401': {'$ref': '#/components/responses/401'},
                '404': {'$ref': '#/components/responses/404'},
                '500': {'$ref': '#/components/responses/500'}
            }
        }
    }
}