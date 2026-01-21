from app.models.vehiculo import Vehiculo
from app.models.conductor import Conductor
from app.models.envio import Envio
from app.models.punto_venta import PuntoVenta
from app.models.destino import Destino
from app.models.envio_calculo import CalculoEnvio
from app.models.ubicacion import Ubicacion
from app.services.graphhopper_service import GraphhopperService
from app.services.peajes_service import PeajesService
from app import db
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import math  # ¡AÑADE ESTO!

class CalculoEnvioService:
    # Configuración por defecto
    PRECIO_GALON = 12000  # Precio por galón de ACPM en COP
    RENDIMIENTO_KM_GALON = 8.0  # Km por galón para camiones
    CATEGORIA_PEAJE = 1  # Categoría 1 para camiones
    
    def __init__(self):
        self.graphhopper = GraphhopperService()
        self.peajes = PeajesService()
    
    def buscar_envios_pendientes(self) -> List[Dict]:
        """Buscar envíos que necesitan asignación"""
        envios = Envio.query.filter_by(estado='pendiente').all()
        
        resultados = []
        for envio in envios:
            resultados.append({
                'envio': envio.to_dict(include_punto_venta=True),
                'punto_venta': envio.punto_venta.to_dict() if envio.punto_venta else None,
                'necesita_asignacion': True
            })
        
        return resultados
    
    def buscar_vehiculos_disponibles(self) -> List[Dict]:
        """Buscar vehículos disponibles con conductor y ubicación"""
        vehiculos = Vehiculo.query.filter(
            Vehiculo.estado == 'disponible',
            Vehiculo.estado_ruta == 'disponible',
            Vehiculo.conductor_id.isnot(None),
            Vehiculo.tipo == 'camion'  # Solo camiones
        ).all()
        
        resultados = []
        for vehiculo in vehiculos:
            resultados.append(vehiculo.to_dict(include_conductor=True, include_ubicacion=True))
        
        return resultados
    
    def calcular_envio(self, envio_id: int, vehiculo_id: int) -> Tuple[Optional[CalculoEnvio], Optional[str]]:
        """Calcular todos los costos para un envío - CORREGIDO"""
        try:
            # Obtener datos del envío
            envio = Envio.query.get(envio_id)
            if not envio:
                return None, "Envío no encontrado"
            
            # Obtener datos del vehículo
            vehiculo = Vehiculo.query.get(vehiculo_id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Verificar que el vehículo tenga conductor
            if not vehiculo.conductor:
                return None, "El vehículo no tiene conductor asignado"
            
            # Obtener coordenadas del punto de venta
            punto_venta = envio.punto_venta
            if not punto_venta:
                return None, "El envío no tiene punto de venta asociado"
            
            origen_lat = float(punto_venta.latitud) if punto_venta.latitud else 0
            origen_lng = float(punto_venta.longitud) if punto_venta.longitud else 0
            
            # Obtener coordenadas reales del destino usando la tabla Destino
            destino_obj = Destino.query.filter_by(ciudad=envio.destino).first()
            if not destino_obj:
                # Intentar buscar por coincidencia parcial si la exacta falla
                destino_obj = Destino.query.filter(Destino.ciudad.ilike(f"%{envio.destino}%")).first()
            
            if not destino_obj:
                return None, f"Destino '{envio.destino}' no encontrado en la base de datos de destinos"
            
            destino_lat = float(destino_obj.latitud)
            destino_lng = float(destino_obj.longitud)
            
            # 1. Obtener ruta de Graphhopper - CORREGIDO
            ruta_info = self.graphhopper.obtener_ruta(
                origen_lat, origen_lng,
                destino_lat, destino_lng,
                vehicle='car'
            )
            
            if 'error' in ruta_info:
                return None, f"Error obteniendo ruta: {ruta_info['error']}"
            
            distancia_km = ruta_info['distancia_km']
            tiempo_minutos = ruta_info['tiempo_minutos']
            puntos_ruta = ruta_info['puntos_ruta']
            
            # 2. Calcular costo de combustible
            galones_necesarios = distancia_km / self.RENDIMIENTO_KM_GALON
            costo_combustible = galones_necesarios * self.PRECIO_GALON
            
            # 3. Calcular costo de peajes
            if puntos_ruta and len(puntos_ruta) > 0:
                peajes_info = self.peajes.calcular_costo_peajes_ruta(
                    puntos_ruta, 
                    categoria=self.CATEGORIA_PEAJE
                )
                costo_peajes = peajes_info['costo_total']
                info_peajes = peajes_info
            else:
                costo_peajes = 0
                info_peajes = {'costo_total': 0, 'cantidad_peajes': 0, 'peajes': []}
            
            # 4. Calcular costo total
            costo_total = costo_combustible + costo_peajes
            
            # 5. Crear registro de cálculo
            calculo = CalculoEnvio(
                envio_id=envio_id,
                vehiculo_id=vehiculo_id,
                conductor_id=vehiculo.conductor_id,
                
                distancia_km=distancia_km,
                tiempo_minutos=tiempo_minutos,
                
                costo_combustible=costo_combustible,
                costo_peajes=costo_peajes,
                costo_total=costo_total,
                
                precio_galon=self.PRECIO_GALON,
                rendimiento_km_galon=self.RENDIMIENTO_KM_GALON,
                
                ruta_json=json.dumps({
                    'puntos_ruta': puntos_ruta,
                    'instrucciones': ruta_info.get('instrucciones', []),
                    'peajes': info_peajes
                }),
                
                origen_lat=origen_lat,
                origen_lng=origen_lng,
                destino_lat=destino_lat,
                destino_lng=destino_lng,
                
                estado='calculado'
            )
            
            db.session.add(calculo)
            db.session.commit()
            
            return calculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def encontrar_mejor_vehiculo(self, envio_id: int) -> List[Dict]:
        """Encontrar los mejores vehículos para un envío"""
        try:
            envio = Envio.query.get(envio_id)
            if not envio:
                return []
            
            punto_venta = envio.punto_venta
            if not punto_venta:
                return []
            
            # Obtener todos los vehículos disponibles
            vehiculos_disponibles = self.buscar_vehiculos_disponibles()
            print(f"DEBUG: Encontrados {len(vehiculos_disponibles)} vehículos disponibles totales (con conductor y tipo camion)")
            
            # Buscar vehículos cercanos (Lógica local)
            vehiculos_cercanos = []
            
            try:
                origen_lat = float(punto_venta.latitud) if punto_venta.latitud else 0
                origen_lng = float(punto_venta.longitud) if punto_venta.longitud else 0
            except (ValueError, TypeError):
                print(f"DEBUG: Error convertiendo coordenadas de punto de venta: {punto_venta.latitud}, {punto_venta.longitud}")
                origen_lat = 0
                origen_lng = 0

            print(f"DEBUG: Buscando cerca de Origen: ({origen_lat}, {origen_lng})")
            
            radio_km = 50.0  # Puedes aumentar esto para probar si es el problema
            
            for v in vehiculos_disponibles:
                v_lat = None
                v_lng = None
                
                # Obtener coordenadas del diccionario de ubicación
                if v.get('ubicacion'):
                    v_lat = v['ubicacion'].get('latitud')
                    v_lng = v['ubicacion'].get('longitud')
                
                if v_lat is not None and v_lng is not None:
                    distancia = self._calcular_distancia_aproximada(
                        origen_lat, origen_lng, 
                        float(v_lat), float(v_lng)
                    )
                    
                    print(f"DEBUG: Vehiculo {v.get('placa')} a {distancia:.2f} km")
                    
                    if distancia <= radio_km:
                        v['distancia_km'] = distancia
                        vehiculos_cercanos.append(v)
                    else:
                        print(f"DEBUG: Vehículo fuera de rango (> {radio_km} km)")
                else:
                    print(f"DEBUG: Vehiculo {v.get('placa')} NO tiene coordenadas validas: {v.get('ubicacion')}")
            
            # Ordenar por distancia (más cercanos primero)
            vehiculos_cercanos.sort(key=lambda x: x.get('distancia_km', float('inf')))
            
            print(f"DEBUG: Total vehículos cercanos encontrados: {len(vehiculos_cercanos)}")
            
            # Calcular propuestas para los 3 vehículos más cercanos
            propuestas = []
            for i, vehiculo in enumerate(vehiculos_cercanos[:3]):  # Solo primeros 3
                calculo, error = self.calcular_envio(envio_id, vehiculo['id'])
                
                if calculo:
                    propuestas.append({
                        'propuesta_id': calculo.id,
                        'vehiculo': vehiculo,
                        'calculo': calculo.to_dict(),
                        'distancia_vehiculo_punto': vehiculo.get('distancia_km', 0),
                        'prioridad': i + 1  # 1 es el más cercano
                    })
            
            return propuestas
            
        except Exception as e:
            print(f"Error encontrando mejor vehículo: {e}")
            return []
    
    def generar_reporte_envio(self, envio_id: int) -> Dict:
        """Generar reporte completo de un envío"""
        try:
            envio = Envio.query.get(envio_id)
            if not envio:
                return {'error': 'Envío no encontrado'}
            
            # Buscar cálculos existentes
            calculos = CalculoEnvio.query.filter_by(envio_id=envio_id).all()
            
            # Generar reporte
            reporte = {
                'envio': envio.to_dict(include_punto_venta=True),
                'resumen': {
                    'peso_carga': float(envio.peso_carga) if envio.peso_carga else 0,
                    'destino': envio.destino,
                    'estado': envio.estado
                },
                'propuestas': [calculo.to_dict() for calculo in calculos],
                'mejor_propuesta': None
            }
            
            # Encontrar la mejor propuesta (menor costo)
            if calculos:
                mejor_calculo = min(calculos, key=lambda x: x.costo_total)
                reporte['mejor_propuesta'] = mejor_calculo.to_dict()
            
            return reporte
            
        except Exception as e:
            return {'error': str(e)}
    
    # ===================== NUEVOS MÉTODOS =====================
    
    def simular_envio(self, origen_lat: float, origen_lng: float, 
                     destino_lat: float, destino_lng: float, 
                     peso_kg: float) -> Dict:
        """Simular un envío completo - ¡ESTE ES EL QUE FALTA!"""
        try:
            # 1. Obtener ruta de Graphhopper
            ruta_info = self.graphhopper.obtener_ruta(
                origen_lat, origen_lng,
                destino_lat, destino_lng,
                vehicle='car'
            )
            
            if 'error' in ruta_info:
                return {'error': ruta_info['error']}
            
            distancia_km = ruta_info['distancia_km']
            puntos_ruta = ruta_info['puntos_ruta']
            
            # 2. Calcular costo de combustible
            galones_necesarios = distancia_km / self.RENDIMIENTO_KM_GALON
            costo_combustible = galones_necesarios * self.PRECIO_GALON
            
            # 3. Calcular costo de peajes
            if puntos_ruta and len(puntos_ruta) > 0:
                peajes_info = self.peajes.calcular_costo_peajes_ruta(
                    puntos_ruta,
                    categoria=self.CATEGORIA_PEAJE
                )
                costo_peajes = peajes_info['costo_total']
            else:
                costo_peajes = 0
                peajes_info = {'costo_total': 0, 'cantidad_peajes': 0, 'peajes': []}
            
            # 4. Calcular costo total
            costo_total = costo_combustible + costo_peajes
            
            # 5. Retornar resultado
            return {
                'simulacion': {
                    'distancia_km': distancia_km,
                    'tiempo_minutos': ruta_info.get('tiempo_minutos', 0),
                    'combustible': {
                        'galones_necesarios': galones_necesarios,
                        'precio_galon': self.PRECIO_GALON,
                        'costo_total': costo_combustible
                    },
                    'peajes': peajes_info,
                    'costo_total': costo_total,
                    'costo_por_kg': costo_total / peso_kg if peso_kg > 0 else 0
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calcular_distancia_aproximada(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcular distancia aproximada en km"""
        # Fórmula simplificada: 1 grado ≈ 111 km
        return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111
    
    def _seleccionar_mejor_vehiculo(self, vehiculos: List[Dict], peso_carga: float, 
                                   distancia_viaje: float, origen_lat: float, origen_lng: float) -> Dict:
        """Seleccionar el mejor vehículo según criterios"""
        if not vehiculos:
            return {}
        
        vehiculos_puntuados = []
        
        for vehiculo in vehiculos:
            puntuacion = 0
            criterios = []
            
            # 1. Capacidad
            capacidad = vehiculo.get('capacidad_kg', 0)
            if capacidad >= peso_carga:
                if capacidad - peso_carga > 0:
                    puntuacion += 40
                    criterios.append('capacidad_adecuada')
                else:
                    puntuacion += 30
                    criterios.append('capacidad_exacta')
            else:
                puntuacion -= 20
                criterios.append('capacidad_insuficiente')
            
            # 2. Proximidad
            vehiculo_lat = None
            vehiculo_lng = None
            
            if vehiculo.get('ubicacion'):
                vehiculo_lat = vehiculo['ubicacion'].get('latitud')
                vehiculo_lng = vehiculo['ubicacion'].get('longitud')
            elif vehiculo.get('ubicacion_lat') and vehiculo.get('ubicacion_lng'):
                # Fallback por si acaso llega plano
                vehiculo_lat = vehiculo.get('ubicacion_lat')
                vehiculo_lng = vehiculo.get('ubicacion_lng')

            if vehiculo_lat and vehiculo_lng:
                distancia = self._calcular_distancia_aproximada(
                    origen_lat, origen_lng,
                    vehiculo_lat, vehiculo_lng
                )
                vehiculo['distancia_origen_km'] = distancia
                
                if distancia < 10:
                    puntuacion += 30
                    criterios.append('proximidad_excelente')
                elif distancia < 50:
                    puntuacion += 20
                    criterios.append('proximidad_buena')
                elif distancia < 100:
                    puntuacion += 10
                    criterios.append('proximidad_aceptable')
            else:
                criterios.append('sin_ubicacion')
            
            # 3. Estado
            if vehiculo.get('estado') == 'disponible':
                puntuacion += 20
                criterios.append('estado_optimo')
            
            # 4. Conductor
            if vehiculo.get('conductor'):
                puntuacion += 10
                criterios.append('conductor_asignado')
            
            vehiculo['puntuacion'] = puntuacion
            vehiculo['criterios'] = criterios
            vehiculos_puntuados.append(vehiculo)
        
        # Seleccionar el mejor
        if vehiculos_puntuados:
            return max(vehiculos_puntuados, key=lambda x: x.get('puntuacion', 0))
        return {}
    
    def _calcular_tiempo_desplazamiento(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcular tiempo estimado de desplazamiento en minutos"""
        distancia = self._calcular_distancia_aproximada(lat1, lng1, lat2, lng2)
        velocidad_promedio = 40  # km/h
        return (distancia / velocidad_promedio) * 60

    def procesar_envios_pendientes(self) -> List[Dict]:
        """
        Procesar MASIVAMENTE todos los envíos pendientes:
        1. Buscar envíos pendientes
        2. Para cada uno, encontrar mejor vehículo
        3. Calcular ruta y costos
        4. Guardar y retornar resultados
        """
        resultados = []
        
        # 1. Buscar envíos pendientes
        envios = Envio.query.filter_by(estado='pendiente').all()
        print(f"Procesando {len(envios)} envios pendientes...")
        
        for envio in envios:
            try:
                print(f" >> Procesando envio ID {envio.id} ({envio.destino})")
                
                # 2. Encontrar mejor vehículo
                propuestas = self.encontrar_mejor_vehiculo(envio.id)
                
                if not propuestas:
                    resultados.append({
                        'envio_id': envio.id,
                        'estado': 'error',
                        'mensaje': 'No se encontraron vehículos disponibles cercanos'
                    })
                    continue
                
                # Tomar la mejor propuesta (la primera, ya viene ordenada)
                mejor_propuesta = propuestas[0]
                vehiculo = mejor_propuesta['vehiculo']
                vehiculo_id = vehiculo['id']
                
                print(f"    Vehículo seleccionado: {vehiculo.get('placa')} (ID {vehiculo_id})")
                
                # 3. Calcular ruta y costos (Guardar en BD)
                calculo, error = self.calcular_envio(envio.id, vehiculo_id)
                
                if error:
                    resultados.append({
                        'envio_id': envio.id,
                        'estado': 'error',
                        'mensaje': error
                    })
                else:
                    # Éxito
                    resultados.append({
                        'envio_id': envio.id,
                        'estado': 'procesado',
                        'vehiculo_asignado': vehiculo,
                        'calculo': calculo.to_dict(),
                        'mensaje': 'Cálculo realizado y guardado exitosamente'
                    })
                    
            except Exception as e:
                print(f"Error procesando envio {envio.id}: {e}")
                resultados.append({
                    'envio_id': envio.id,
                    'estado': 'error',
                    'mensaje': str(e)
                })
        
        return resultados