import yaml
from app.docs.vehiculo_docs import vehiculo_swagger
from app.docs.conductor_docs import conductor_swagger
from app.docs.usuario_docs import usuario_swagger
from app.docs.estadisticas_docs import estadisticas_swagger

SWAGGER_TEMPLATE = {
    'openapi': '3.0.0',
    'info': {
        'title': 'API Sistema de Transporte',
        'description': 'API para gestión de vehículos, conductores y usuarios de transporte',
        'version': '1.0.0',
        'contact': {
            'name': 'Soporte Técnico',
            'email': 'soporte@sistema-transporte.com'
        }
    },
    'servers': [
        {
            'url': 'http://localhost:5000',
            'description': 'Servidor de desarrollo'
        }
    ],
    'tags': [
        {'name': 'Vehículos', 'description': 'Operaciones con vehículos'},
        {'name': 'Conductores', 'description': 'Operaciones con conductores'},
        {'name': 'Usuarios', 'description': 'Operaciones con usuarios de la app'},
        {'name': 'Estadísticas', 'description': 'Estadísticas del sistema'},
        {'name': 'Sistema', 'description': 'Endpoints del sistema'}
    ],
    'paths': {},
    'components': {
        'schemas': {
            'Error': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'description': 'Mensaje de error'
                    }
                }
            },
            'Success': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'Mensaje de éxito'
                    }
                }
            }
        }
    }
}

def generate_swagger_spec():
    """Generar especificación completa de Swagger"""
    swagger_spec = SWAGGER_TEMPLATE.copy()
    
    # Combinar todos los paths
    for spec in [vehiculo_swagger, conductor_swagger, usuario_swagger, estadisticas_swagger]:
        swagger_spec['paths'].update(spec)
    
    return swagger_spec

def save_swagger_yaml():
    """Guardar especificación Swagger en archivo YAML"""
    swagger_spec = generate_swagger_spec()
    
    with open('static/swagger.yaml', 'w') as file:
        yaml.dump(swagger_spec, file, default_flow_style=False)
    
    return swagger_spec