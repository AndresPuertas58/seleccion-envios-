from flask import Blueprint, jsonify, request
from app.services.calculo_service import CalculoEnvioService
from app.services.graphhopper_service import GraphhopperService
from app.services.peajes_service import PeajesService
from datetime import datetime

calculo_bp = Blueprint('calculo', __name__, url_prefix='/api/calculo')

@calculo_bp.route('/envios-pendientes', methods=['GET'])
def get_envios_pendientes():
    """Obtener envíos que necesitan asignación"""
    try:    
        servicio = CalculoEnvioService()
        envios = servicio.buscar_envios_pendientes()
        
        return jsonify({
            'total': len(envios),
            'envios': envios
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/vehiculos-disponibles', methods=['GET'])
def get_vehiculos_disponibles():
    """Obtener vehículos disponibles con conductor"""
    try:
        servicio = CalculoEnvioService()
        vehiculos = servicio.buscar_vehiculos_disponibles()
        
        return jsonify({
            'total': len(vehiculos),
            'vehiculos': vehiculos
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/calcular-envio', methods=['POST'])
def calcular_envio():
    """Calcular costo y ruta para un envío específico"""
    try:
        data = request.json
        
        if 'envio_id' not in data or 'vehiculo_id' not in data:
            return jsonify({'error': 'Se requieren envio_id y vehiculo_id'}), 400
        
        servicio = CalculoEnvioService()
        calculo, error = servicio.calcular_envio(data['envio_id'], data['vehiculo_id'])
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'message': 'Cálculo realizado exitosamente',
            'data': calculo.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/encontrar-mejor-vehiculo/<int:envio_id>', methods=['GET'])
def encontrar_mejor_vehiculo(envio_id):
    """Encontrar el mejor vehículo para un envío"""
    try:
        servicio = CalculoEnvioService()
        propuestas = servicio.encontrar_mejor_vehiculo(envio_id)
        
        return jsonify({
            'envio_id': envio_id,
            'total_propuestas': len(propuestas),
            'propuestas': propuestas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/reporte-envio/<int:envio_id>', methods=['GET'])
def get_reporte_envio(envio_id):
    """Obtener reporte completo de un envío"""
    try:
        servicio = CalculoEnvioService()
        reporte = servicio.generar_reporte_envio(envio_id)
        
        if 'error' in reporte:
            return jsonify(reporte), 404
        
        return jsonify(reporte)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/obtener-ruta', methods=['POST'])
def obtener_ruta():
    """Obtener ruta entre dos puntos (para pruebas)"""
    try:
        data = request.json
        
        if not all(k in data for k in ['origen_lat', 'origen_lng', 'destino_lat', 'destino_lng']):
            return jsonify({'error': 'Se requieren coordenadas de origen y destino'}), 400
        
        graphhopper = GraphhopperService()
        ruta = graphhopper.obtener_ruta(
        data['origen_lat'], data['origen_lng'],
        data['destino_lat'], data['destino_lng'],
        vehicle='car'  # Cambia 'truck' por 'car' si 'truck' no existe en Graphhopper
        )
        
        return jsonify(ruta)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/calcular-peajes', methods=['POST'])
def calcular_peajes():
    """Calcular peajes para una ruta usando la base de datos local"""
    try:
        data = request.json
        
        if 'puntos_ruta' not in data:
            return jsonify({'error': 'Se requieren puntos_ruta'}), 400
        
        servicio = PeajesService()
        categoria = data.get('categoria', 1)
        
        resultado = servicio.calcular_costo_peajes_ruta(
            data['puntos_ruta'],
            categoria=categoria
        )
        
        return jsonify({
            'success': True,
            'costo_total': resultado['costo_total'],
            'cantidad_peajes': resultado['cantidad_peajes'],
            'peajes': resultado['peajes'],
            'categoria': categoria
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculo_bp.route('/simular-envio', methods=['POST'])
def simular_envio():
    """Simular un envío completo con vehículos de ubicaciones reales"""
    try:
        data = request.json
        
        campos_requeridos = ['origen_lat', 'origen_lng', 'destino_lat', 'destino_lng', 'peso_kg']
        faltantes = [campo for campo in campos_requeridos if campo not in data]
        
        if faltantes:
            return jsonify({'error': f'Faltan campos: {", ".join(faltantes)}'}), 400
        
        servicio = CalculoEnvioService()
        peso_carga = float(data['peso_kg'])
        
        # 1. Simular cálculo de envío
        resultado = servicio.simular_envio(
            data['origen_lat'], data['origen_lng'],
            data['destino_lat'], data['destino_lng'],
            peso_carga
        )
        
        if 'error' in resultado:
            return jsonify({'error': resultado['error']}), 400
        
        # 2. Buscar vehículos disponibles con ubicaciones
        vehiculos_disponibles = servicio.buscar_vehiculos_disponibles()
        
        if not vehiculos_disponibles:
            return jsonify({
                'success': True,
                'advertencia': 'No hay vehículos disponibles',
                'simulacion': resultado['simulacion'],
                'asignacion': None
            })
        
        # 3. Calcular distancia del viaje
        distancia_viaje = servicio._calcular_distancia_aproximada(
            data['origen_lat'], data['origen_lng'],
            data['destino_lat'], data['destino_lng']
        )
        
        # 4. Seleccionar el mejor vehículo
        vehiculo_seleccionado = servicio._seleccionar_mejor_vehiculo(
            vehiculos_disponibles,
            peso_carga,
            distancia_viaje,
            data['origen_lat'],
            data['origen_lng']
        )
        
        # 5. Preparar información detallada
        simulacion = resultado['simulacion']
        
        # Información del vehículo seleccionado
        info_vehiculo = {
            'vehiculo_asignado': {
                'detalles_generales': {
                    'id': vehiculo_seleccionado.get('id'),
                    'placa': vehiculo_seleccionado.get('placa', 'N/A'),
                    'marca': vehiculo_seleccionado.get('marca', 'N/A'),
                    'modelo': vehiculo_seleccionado.get('modelo', 'N/A'),
                    'tipo': vehiculo_seleccionado.get('tipo', 'camion'),
                    'color': vehiculo_seleccionado.get('color', 'N/A'),
                    'estado_operativo': vehiculo_seleccionado.get('estado', 'disponible'),
                    'estado_ruta': vehiculo_seleccionado.get('estado_ruta', 'disponible')
                },
                'capacidad_carga': {
                    'capacidad_maxima_kg': vehiculo_seleccionado.get('capacidad_kg', 0),
                    'peso_solicitado_kg': peso_carga,
                    'disponibilidad_carga_kg': max(0, vehiculo_seleccionado.get('capacidad_kg', 0) - peso_carga),
                    'porcentaje_utilizacion': (peso_carga / vehiculo_seleccionado.get('capacidad_kg', 1)) * 100 if vehiculo_seleccionado.get('capacidad_kg', 0) > 0 else 0
                },
                'ubicacion_actual': {
                    'coordenadas': {
                        'latitud': vehiculo_seleccionado.get('ubicacion_lat'),
                        'longitud': vehiculo_seleccionado.get('ubicacion_lng')
                    },
                    'direccion_completa': vehiculo_seleccionado.get('ubicacion_completa', {}),
                    'distancia_al_origen_km': round(vehiculo_seleccionado.get('distancia_origen_km', 0), 2)
                },
                'analisis_seleccion': {
                    'puntuacion_total': vehiculo_seleccionado.get('puntuacion', 0),
                    'criterios_aplicados': vehiculo_seleccionado.get('criterios', []),
                    'posicion_ranking': 1,
                    'total_vehiculos_evaluados': len(vehiculos_disponibles)
                }
            },
            'conductor_asignado': {
                'detalles_personales': {
                    'id': vehiculo_seleccionado.get('conductor', {}).get('id'),
                    'nombre_completo': vehiculo_seleccionado.get('conductor', {}).get('nombre', 'Por asignar'),
                    'numero_documento': vehiculo_seleccionado.get('conductor', {}).get('documento', 'N/A'),
                    'licencia_conduccion': vehiculo_seleccionado.get('conductor', {}).get('licencia', 'N/A'),
                    'telefono_contacto': vehiculo_seleccionado.get('conductor', {}).get('telefono', 'N/A'),
                    'estado': 'disponible'
                },
                'disponibilidad': 'inmediata' if vehiculo_seleccionado.get('estado') == 'disponible' else 'programada'
            }
        }
        
        # 6. Calcular tiempos con ubicación real
        tiempo_total = simulacion['tiempo_minutos']
        if vehiculo_seleccionado.get('ubicacion_lat') and vehiculo_seleccionado.get('ubicacion_lng'):
            tiempo_desplazamiento = servicio._calcular_tiempo_desplazamiento(
                vehiculo_seleccionado['ubicacion_lat'],
                vehiculo_seleccionado['ubicacion_lng'],
                data['origen_lat'],
                data['origen_lng']
            )
            tiempo_total += tiempo_desplazamiento
        
        # 7. Retornar respuesta completa
        return jsonify({
            'success': True,
            'metadatos': {
                'timestamp': datetime.now().isoformat(),
                'origen': f"({data['origen_lat']}, {data['origen_lng']})",
                'destino': f"({data['destino_lat']}, {data['destino_lng']})",
                'peso_carga_kg': peso_carga
            },
            'resumen_ejecutivo': {
                'distancia_total_km': round(simulacion['distancia_km'], 2),
                'tiempo_total_estimado_minutos': round(tiempo_total, 0),
                'costo_total_estimado': round(simulacion['costo_total'], 2),
                'costo_por_kg': round(simulacion['costo_por_kg'], 2),
                'viabilidad': 'alta' if vehiculo_seleccionado.get('puntuacion', 0) > 60 else 'media'
            },
            'analisis_costos': {
                'combustible': simulacion['combustible'],
                'peajes': simulacion['peajes'],
                'costo_total': simulacion['costo_total']
            },
            'asignacion_recurso': info_vehiculo,
            'linea_tiempo_estimada': {
                'desplazamiento_vehiculo_origen': {
                    'distancia_km': round(vehiculo_seleccionado.get('distancia_origen_km', 0), 2),
                    'tiempo_minutos': round(vehiculo_seleccionado.get('distancia_origen_km', 0) / 40 * 60, 0) if vehiculo_seleccionado.get('distancia_origen_km') else 0,
                    'actividad': 'Desplazamiento del vehículo al punto de origen'
                },
                'carga_mercancia': {
                    'tiempo_minutos': 45,
                    'actividad': 'Carga y verificación de mercancía'
                },
                'transporte_principal': {
                    'distancia_km': round(simulacion['distancia_km'], 2),
                    'tiempo_minutos': round(simulacion['tiempo_minutos'], 0),
                    'actividad': 'Transporte principal al destino'
                },
                'descarga_mercancia': {
                    'tiempo_minutos': 30,
                    'actividad': 'Descarga y entrega de mercancía'
                },
                'tiempo_total_operacion_minutos': round(tiempo_total + 75, 0)  # +75 min para carga y descarga
            },
            'alternativas_disponibles': {
                'total_vehiculos_disponibles': len(vehiculos_disponibles),
                'mejores_alternativas': [
                    {
                        'placa': v.get('placa'),
                        'puntuacion': v.get('puntuacion', 0),
                        'distancia_origen_km': v.get('distancia_origen_km', 0),
                        'capacidad_kg': v.get('capacidad_kg', 0)
                    }
                    for v in vehiculos_disponibles[1:3]  # Mostrar siguientes 2 mejores
                ] if len(vehiculos_disponibles) > 1 else []
            },
            'recomendaciones_operativas': [
                'Confirmar disponibilidad del conductor asignado',
                'Verificar documentación del vehículo',
                'Programar hora exacta de carga',
                'Informar al conductor sobre peajes en la ruta'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500