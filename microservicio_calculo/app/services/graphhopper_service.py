import requests
import json
from typing import Dict

class GraphhopperService:
    def __init__(self, base_url: str = "http://localhost:8989"):
        self.base_url = base_url
    
    def obtener_ruta(self, origen_lat: float, origen_lng: float, 
                    destino_lat: float, destino_lng: float,
                    vehicle: str = "car") -> Dict:
        """Obtener ruta entre dos puntos usando Graphhopper LOCAL"""
        try:
            # URL para Graphhopper local API v1
            url = f"{self.base_url}/route"
            
            # Parámetros para Graphhopper v1
            params = {
                'point': [f"{origen_lat},{origen_lng}", f"{destino_lat},{destino_lng}"],
                'profile': vehicle,  # 'profile' en lugar de 'vehicle' en v1
                'points_encoded': False,
                'instructions': False,
                'elevation': False
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'paths' in data and len(data['paths']) > 0:
                    path = data['paths'][0]
                    
                    puntos_ruta = []
                    if 'points' in path and 'coordinates' in path['points']:
                        for coord in path['points']['coordinates']:
                            puntos_ruta.append({
                                'lat': coord[1],
                                'lng': coord[0]
                            })
                    
                    return {
                        'success': True,
                        'distancia_km': path.get('distance', 0) / 1000,
                        'tiempo_minutos': path.get('time', 0) / 60000,
                        'puntos_ruta': puntos_ruta,
                        'ascenso': path.get('ascend', 0),
                        'descenso': path.get('descend', 0)
                    }
            
            # Si falla, intentar con método POST
            return self._obtener_ruta_post(origen_lat, origen_lng, destino_lat, destino_lng, vehicle)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'distancia_km': 0,
                'tiempo_minutos': 0,
                'puntos_ruta': []
            }
    
    def _obtener_ruta_post(self, origen_lat: float, origen_lng: float,
                          destino_lat: float, destino_lng: float,
                          vehicle: str = "car") -> Dict:
        """Método alternativo usando POST"""
        try:
            url = f"{self.base_url}/route"
            
            payload = {
                "points": [
                    [origen_lng, origen_lat],  # Graphhopper usa [lng, lat]
                    [destino_lng, destino_lat]
                ],
                "profile": vehicle,
                "points_encoded": False,
                "instructions": False
            }
            
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'paths' in data and len(data['paths']) > 0:
                    path = data['paths'][0]
                    
                    puntos_ruta = []
                    if 'points' in path and 'coordinates' in path['points']:
                        for coord in path['points']['coordinates']:
                            puntos_ruta.append({
                                'lat': coord[1],
                                'lng': coord[0]
                            })
                    
                    return {
                        'success': True,
                        'distancia_km': path.get('distance', 0) / 1000,
                        'tiempo_minutos': path.get('time', 0) / 60000,
                        'puntos_ruta': puntos_ruta,
                        'ascenso': path.get('ascend', 0),
                        'descenso': path.get('descend', 0)
                    }
            
            return {
                'success': False,
                'error': f'Error {response.status_code}: {response.text[:100]}',
                'distancia_km': 0,
                'tiempo_minutos': 0,
                'puntos_ruta': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'distancia_km': 0,
                'tiempo_minutos': 0,
                'puntos_ruta': []
            }
    
    def verificar_conexion(self) -> Dict:
        """Verificar que Graphhopper está funcionando"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                return {
                    'conectado': True,
                    'version': 'Graphhopper local',
                    'status': 'OK'
                }
            else:
                return {
                    'conectado': False,
                    'error': f'Status code: {response.status_code}'
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'conectado': False,
                'error': 'No se puede conectar a Graphhopper'
            }
        except Exception as e:
            return {
                'conectado': False,
                'error': str(e)
            }