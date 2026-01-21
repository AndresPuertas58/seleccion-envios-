# Documentación para estadísticas
estadisticas_docs = {
    'get_estadisticas': 'Obtener estadísticas del sistema',
    'health_check': 'Verificar estado del sistema'
}

estadisticas_swagger = {
    '/api/estadisticas': {
        'get': {
            'tags': ['Estadísticas'],
            'summary': 'Obtener estadísticas del sistema',
            'responses': {
                '200': {
                    'description': 'Estadísticas del sistema',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'vehiculos': {
                                        'type': 'object',
                                        'properties': {
                                            'total': {'type': 'integer'},
                                            'disponibles': {'type': 'integer'},
                                            'en_uso': {'type': 'integer'},
                                            'mantenimiento': {'type': 'integer'}
                                        }
                                    },
                                    'conductores': {
                                        'type': 'object',
                                        'properties': {
                                            'total': {'type': 'integer'},
                                            'activos': {'type': 'integer'},
                                            'inactivos': {'type': 'integer'}
                                        }
                                    },
                                    'usuarios': {
                                        'type': 'object',
                                        'properties': {
                                            'total': {'type': 'integer'},
                                            'activos': {'type': 'integer'},
                                            'inactivos': {'type': 'integer'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    '/api/health': {
        'get': {
            'tags': ['Sistema'],
            'summary': 'Verificar estado del sistema',
            'responses': {
                '200': {
                    'description': 'Sistema saludable',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'status': {'type': 'string'},
                                    'database': {'type': 'string'},
                                    'timestamp': {'type': 'string', 'format': 'date-time'}
                                }
                            }
                        }
                    }
                },
                '500': {
                    'description': 'Sistema no saludable',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'status': {'type': 'string'},
                                    'database': {'type': 'string'},
                                    'error': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}