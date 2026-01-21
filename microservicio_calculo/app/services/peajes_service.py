# app/services/peajes_service.py
from app.models.peaje import Peaje
from app import db
from typing import List, Dict
import math

class PeajesService:
    
    def __init__(self):
        pass  # No necesita configuración especial
    
    def calcular_costo_peajes_ruta(self, puntos_ruta: List[Dict], categoria: int = 1) -> Dict:
        """
        Calcular peajes para una ruta usando la base de datos local
        
        Args:
            puntos_ruta: Lista de puntos de la ruta [{"lat": x, "lng": y}, ...]
            categoria: Categoría del vehículo (1-5)
        
        Returns:
            Dict con costo total, cantidad de peajes y lista de peajes
        """
        try:
            print(f"📍 Buscando peajes para ruta con {len(puntos_ruta)} puntos, categoría {categoria}")
            
            if not puntos_ruta or len(puntos_ruta) < 2:
                return self._resultado_vacio(categoria)
            
            # 1. Obtener todos los peajes en el área de la ruta
            peajes_en_area = self._obtener_peajes_en_area(puntos_ruta)
            
            if not peajes_en_area:
                print("ℹ️  No se encontraron peajes en el área")
                return self._resultado_vacio(categoria)
            
            print(f"📊 Encontrados {len(peajes_en_area)} peajes en el área")
            
            # 2. Filtrar peajes que están cerca de la ruta
            peajes_cercanos = self._filtrar_peajes_cerca_ruta(peajes_en_area, puntos_ruta)
            
            # 3. Calcular costos
            costo_total = 0
            peajes_encontrados = []
            
            for peaje in peajes_cercanos:
                precio = peaje.get_precio_categoria(categoria)
                if precio > 0:
                    costo_total += precio
                    peajes_encontrados.append({
                        'id': peaje.id,
                        'nombre': peaje.nombrepeaje or 'Peaje',
                        'costo': precio,
                        'ubicacion': peaje.ubicacion or f"Lat: {peaje.latitud}, Lng: {peaje.longitud}",
                        'sector': peaje.sector,
                        'lat': float(peaje.latitud) if peaje.latitud else None,
                        'lng': float(peaje.longitud) if peaje.longitud else None
                    })
            
            print(f"✅ Encontrados {len(peajes_encontrados)} peajes en la ruta, costo total: ${costo_total:,}")
            
            return {
                'costo_total': costo_total,
                'cantidad_peajes': len(peajes_encontrados),
                'peajes': peajes_encontrados,
                'categoria': categoria
            }
            
        except Exception as e:
            print(f"❌ Error calculando peajes: {e}")
            return self._resultado_vacio(categoria, str(e))
    
    def _obtener_peajes_en_area(self, puntos_ruta: List[Dict]) -> List[Peaje]:
        """Obtener peajes dentro del área de la ruta"""
        try:
            # Calcular bounding box de la ruta
            lats = [p['lat'] for p in puntos_ruta if 'lat' in p]
            lngs = [p['lng'] for p in puntos_ruta if 'lng' in p]
            
            if not lats or not lngs:
                return []
            
            min_lat, max_lat = min(lats), max(lats)
            min_lng, max_lng = min(lngs), max(lngs)
            
            # Expandir un poco el área de búsqueda
            padding = 0.2  # ~22km
            min_lat -= padding
            max_lat += padding
            min_lng -= padding
            max_lng += padding
            
            # Consultar peajes en el área
            peajes = Peaje.query.filter(
                Peaje.latitud.between(min_lat, max_lat),
                Peaje.longitud.between(min_lng, max_lng)
            ).limit(100).all()
            
            return peajes
            
        except Exception as e:
            print(f"Error obteniendo peajes en área: {e}")
            return []
    
    def _filtrar_peajes_cerca_ruta(self, peajes: List[Peaje], puntos_ruta: List[Dict], 
                                  max_distancia_km: float = 5.0) -> List[Peaje]:
        """Filtrar peajes que están cerca de la ruta"""
        try:
            peajes_cercanos = []
            max_distancia_metros = max_distancia_km * 1000
            
            for peaje in peajes:
                if not peaje.latitud or not peaje.longitud:
                    continue
                    
                # Calcular distancia mínima del peaje a cualquier punto de la ruta
                min_distancia = float('inf')
                lat_peaje = float(peaje.latitud)
                lng_peaje = float(peaje.longitud)
                
                for punto in puntos_ruta:
                    if 'lat' in punto and 'lng' in punto:
                        distancia = self._calcular_distancia_metros(
                            lat_peaje, lng_peaje,
                            punto['lat'], punto['lng']
                        )
                        if distancia < min_distancia:
                            min_distancia = distancia
                
                # Si está dentro de la distancia máxima, agregarlo
                if min_distancia <= max_distancia_metros:
                    peajes_cercanos.append(peaje)
            
            return peajes_cercanos
            
        except Exception as e:
            print(f"Error filtrando peajes: {e}")
            return []
    
    def _calcular_distancia_metros(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcular distancia aproximada en metros (fórmula Haversine simplificada)"""
        # Radio de la Tierra en metros
        R = 6371000
        
        # Convertir a radianes
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        # Fórmula Haversine
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    def _resultado_vacio(self, categoria: int, error: str = None) -> Dict:
        """Resultado vacío por defecto"""
        resultado = {
            'costo_total': 0,
            'cantidad_peajes': 0,
            'peajes': [],
            'categoria': categoria
        }
        if error:
            resultado['error'] = error
        return resultado
    
    # Método adicional para búsqueda rápida
    def buscar_peajes_cercanos(self, lat: float, lng: float, radio_km: float = 10.0) -> List[Dict]:
        """Buscar peajes cercanos a una ubicación"""
        try:
            # Calcular bounding box
            radio_grados = radio_km / 111.0  # Aprox 1° = 111km
            
            peajes = Peaje.query.filter(
                Peaje.latitud.between(lat - radio_grados, lat + radio_grados),
                Peaje.longitud.between(lng - radio_grados, lng + radio_grados)
            ).limit(50).all()
            
            return [peaje.to_dict() for peaje in peajes]
            
        except Exception as e:
            print(f"Error buscando peajes cercanos: {e}")
            return []