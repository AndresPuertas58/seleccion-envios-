from app.models.punto_venta import PuntoVenta
from app import db
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class PuntoVentaService:
    @staticmethod
    def get_all() -> List[PuntoVenta]:
        """Obtener todos los puntos de venta"""
        return PuntoVenta.query.order_by(PuntoVenta.nombre).all()
    
    @staticmethod
    def get_by_id(id: int) -> Optional[PuntoVenta]:
        """Obtener punto de venta por ID"""
        return PuntoVenta.query.get(id)
    
    @staticmethod
    def get_active() -> List[PuntoVenta]:
        """Obtener puntos de venta activos"""
        return PuntoVenta.query.filter_by(estado='activo').all()
    
    @staticmethod
    def create(data: Dict) -> Tuple[Optional[PuntoVenta], Optional[str]]:
        """Crear un nuevo punto de venta"""
        try:
            # Validar campos requeridos
            campos_requeridos = ['nombre', 'latitud', 'longitud']
            for campo in campos_requeridos:
                if campo not in data:
                    return None, f"Campo requerido: {campo}"
            
            # Validar coordenadas
            try:
                latitud = float(data['latitud'])
                longitud = float(data['longitud'])
                
                if not (-90 <= latitud <= 90):
                    return None, "Latitud fuera de rango (-90 a 90)"
                if not (-180 <= longitud <= 180):
                    return None, "Longitud fuera de rango (-180 a 180)"
            except (ValueError, TypeError):
                return None, "Latitud y longitud deben ser números válidos"
            
            # Crear punto de venta
            punto_venta = PuntoVenta(
                nombre=data['nombre'],
                ubicacion=data.get('ubicacion', 'Bogotá'),
                latitud=latitud,
                longitud=longitud,
                barrio=data.get('barrio'),
                encargado=data.get('encargado'),
                telefono=data.get('telefono'),
                email=data.get('email'),
                estado=data.get('estado', 'activo')
            )
            
            db.session.add(punto_venta)
            db.session.commit()
            return punto_venta, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_nearby(latitud: float, longitud: float, radio_km: float = 5.0) -> List[PuntoVenta]:
        """Obtener puntos de venta cercanos a una ubicación"""
        # Fórmula Haversine aproximada
        query = """
        SELECT p.*,
            (6371 * acos(
                cos(radians(:lat)) * cos(radians(p.latitud)) * 
                cos(radians(p.longitud) - radians(:lon)) + 
                sin(radians(:lat)) * sin(radians(p.latitud))
            )) as distancia_km
        FROM puntos_venta p
        WHERE p.estado = 'activo'
        HAVING distancia_km <= :radio
        ORDER BY distancia_km
        """
        
        try:
            resultados = db.session.execute(
                query, 
                {'lat': latitud, 'lon': longitud, 'radio': radio_km}
            ).fetchall()
            
            puntos_venta = []
            for row in resultados:
                punto_dict = dict(row)
                punto = PuntoVenta.query.get(punto_dict['id'])
                if punto:
                    setattr(punto, 'distancia_km', punto_dict['distancia_km'])
                    puntos_venta.append(punto)
            
            return puntos_venta
        except Exception as e:
            print(f"Error en búsqueda cercana: {e}")
            return []