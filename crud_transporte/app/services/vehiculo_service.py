from app.models.vehiculo import Vehiculo
from app.models.ubicacion import Ubicacion
from app import db
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class VehiculoService:
    @staticmethod
    def get_all(with_ubicacion: bool = False) -> List[Vehiculo]:
        """Obtener todos los vehículos"""
        query = Vehiculo.query
        
        if with_ubicacion:
            query = query.options(db.joinedload(Vehiculo.ubicacion))
        
        return query.all()
    
    @staticmethod
    def get_by_id(id: int, with_ubicacion: bool = False) -> Optional[Vehiculo]:
        """Obtener vehículo por ID"""
        query = Vehiculo.query
        
        if with_ubicacion:
            query = query.options(db.joinedload(Vehiculo.ubicacion))
        
        return query.get(id)
    
    @staticmethod
    def get_by_tipo(tipo: str, solo_disponibles: bool = True, with_ubicacion: bool = True) -> List[Vehiculo]:
        """Obtener vehículos por tipo"""
        query = Vehiculo.query.filter_by(tipo=tipo)
        
        if solo_disponibles:
            query = query.filter_by(estado='disponible', estado_ruta='disponible')
        
        if with_ubicacion:
            query = query.options(db.joinedload(Vehiculo.ubicacion))
        
        return query.all()
    
    @staticmethod
    def get_camiones_disponibles(with_ubicacion: bool = True) -> List[Vehiculo]:
        """Obtener camiones disponibles específicamente"""
        return VehiculoService.get_by_tipo('camion', solo_disponibles=True, with_ubicacion=with_ubicacion)
    
    @staticmethod
    def create(data: Dict) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Crear un nuevo vehículo"""
        try:
            # Validar campos requeridos
            campos_requeridos = ['tipo', 'modelo', 'codigo_serial']
            for campo in campos_requeridos:
                if campo not in data:
                    return None, f"Campo requerido: {campo}"
            
            # Crear vehículo
            vehiculo = Vehiculo(
                tipo=data['tipo'],
                marca=data.get('marca', ''),
                modelo=data['modelo'],
                codigo_serial=data['codigo_serial'],
                placa=data.get('placa', ''),
                color=data.get('color', ''),
                estado=data.get('estado', 'disponible'),
                estado_ruta=data.get('estado_ruta', 'disponible'),
                conductor_id=data.get('conductor_id')
            )
            
            # Fechas
            if 'fecha_adquisicion' in data and data['fecha_adquisicion']:
                vehiculo.fecha_adquisicion = datetime.strptime(data['fecha_adquisicion'], '%Y-%m-%d')
            
            if 'ultimo_mantenimiento' in data and data['ultimo_mantenimiento']:
                vehiculo.ultimo_mantenimiento = datetime.strptime(data['ultimo_mantenimiento'], '%Y-%m-%d')
            
            db.session.add(vehiculo)
            db.session.flush()  # Para obtener el ID
            
            # Crear ubicación si se proporciona
            if all(k in data for k in ['latitud', 'longitud']):
                ubicacion = Ubicacion(
                    vehiculo_id=vehiculo.id,
                    latitud=data['latitud'],
                    longitud=data['longitud'],
                    direccion=data.get('direccion', ''),
                    barrio=data.get('barrio', ''),
                    ciudad=data.get('ciudad', 'Bogotá')
                )
                db.session.add(ubicacion)
            
            db.session.commit()
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update(id: int, data: Dict) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Actualizar vehículo"""
        try:
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Campos del vehículo
            campos_vehiculo = ['tipo', 'marca', 'modelo', 'codigo_serial', 
                              'placa', 'color', 'estado', 'estado_ruta', 'conductor_id']
            
            for campo in campos_vehiculo:
                if campo in data:
                    setattr(vehiculo, campo, data[campo])
            
            # Fechas
            if 'fecha_adquisicion' in data:
                vehiculo.fecha_adquisicion = datetime.strptime(data['fecha_adquisicion'], '%Y-%m-%d') if data['fecha_adquisicion'] else None
            
            if 'ultimo_mantenimiento' in data:
                vehiculo.ultimo_mantenimiento = datetime.strptime(data['ultimo_mantenimiento'], '%Y-%m-%d') if data['ultimo_mantenimiento'] else None
            
            # Actualizar ubicación si se proporciona
            if any(k in data for k in ['latitud', 'longitud', 'direccion', 'barrio']):
                ubicacion = Ubicacion.query.filter_by(vehiculo_id=id).first()
                
                if ubicacion:
                    # Actualizar ubicación existente
                    if 'latitud' in data:
                        ubicacion.latitud = data['latitud']
                    if 'longitud' in data:
                        ubicacion.longitud = data['longitud']
                    if 'direccion' in data:
                        ubicacion.direccion = data['direccion']
                    if 'barrio' in data:
                        ubicacion.barrio = data['barrio']
                    if 'ciudad' in data:
                        ubicacion.ciudad = data['ciudad']
                    ubicacion.ultima_actualizacion = datetime.utcnow()
                else:
                    # Crear nueva ubicación
                    if all(k in data for k in ['latitud', 'longitud']):
                        ubicacion = Ubicacion(
                            vehiculo_id=id,
                            latitud=data['latitud'],
                            longitud=data['longitud'],
                            direccion=data.get('direccion', ''),
                            barrio=data.get('barrio', ''),
                            ciudad=data.get('ciudad', 'Bogotá')
                        )
                        db.session.add(ubicacion)
            
            db.session.commit()
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete(id: int) -> Tuple[bool, Optional[str]]:
        """Eliminar vehículo"""
        try:
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return False, "Vehículo no encontrado"
            
            # Nota: La ubicación se eliminará automáticamente por CASCADE
            db.session.delete(vehiculo)
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_estadisticas() -> Dict:
        """Obtener estadísticas de vehículos"""
        total = Vehiculo.query.count()
        
        estadisticas = {
            'total': total,
            'disponibles': Vehiculo.query.filter_by(estado='disponible', estado_ruta='disponible').count(),
            'en_uso': Vehiculo.query.filter_by(estado='en_uso').count(),
            'mantenimiento': Vehiculo.query.filter_by(estado='mantenimiento').count(),
            'desactivados': Vehiculo.query.filter_by(estado='desactivado').count(),
            'por_tipo': {}
        }
        
        # Estadísticas por tipo
        tipos = db.session.query(Vehiculo.tipo, db.func.count(Vehiculo.id)).group_by(Vehiculo.tipo).all()
        for tipo, cantidad in tipos:
            estadisticas['por_tipo'][tipo] = cantidad
        
        # Porcentajes
        if total > 0:
            estadisticas['porcentaje_disponibles'] = round((estadisticas['disponibles'] / total) * 100, 2)
        else:
            estadisticas['porcentaje_disponibles'] = 0
        
        return estadisticas
    
    @staticmethod
    def cambiar_estado(id: int, nuevo_estado: str) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Cambiar estado de un vehículo"""
        try:
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Validar estado
            estados_validos = ['disponible', 'en_uso', 'mantenimiento', 'desactivado']
            if nuevo_estado not in estados_validos:
                return None, f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
            
            # Cambiar estado
            vehiculo.estado = nuevo_estado
            vehiculo.updated_at = datetime.utcnow()
            
            # Si se marca como desactivado, también cambiar estado_ruta
            if nuevo_estado == 'desactivado':
                vehiculo.estado_ruta = 'disponible'
            
            db.session.commit()
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def cambiar_estado_ruta(id: int, nuevo_estado_ruta: str) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Cambiar estado de ruta de un vehículo"""
        try:
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Validar estado_ruta
            estados_validos = ['disponible', 'en_ruta', 'cargando', 'mantenimiento']
            if nuevo_estado_ruta not in estados_validos:
                return None, f"Estado de ruta inválido. Estados válidos: {', '.join(estados_validos)}"
            
            # Cambiar estado_ruta
            vehiculo.estado_ruta = nuevo_estado_ruta
            vehiculo.updated_at = datetime.utcnow()
            
            db.session.commit()
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def actualizar_ubicacion(id: int, latitud: float, longitud: float, 
                            direccion: str = None, barrio: str = None, ciudad: str = 'Bogotá') -> Tuple[bool, Optional[str]]:
        """Actualizar o crear ubicación de un vehículo"""
        try:
            # Verificar que el vehículo existe
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return False, "Vehículo no encontrado"
            
            # Buscar ubicación existente
            ubicacion = Ubicacion.query.filter_by(vehiculo_id=id).first()
            
            if ubicacion:
                # Actualizar ubicación existente
                ubicacion.latitud = latitud
                ubicacion.longitud = longitud
                if direccion:
                    ubicacion.direccion = direccion
                if barrio:
                    ubicacion.barrio = barrio
                ubicacion.ciudad = ciudad
                ubicacion.ultima_actualizacion = datetime.utcnow()
            else:
                # Crear nueva ubicación
                ubicacion = Ubicacion(
                    vehiculo_id=id,
                    latitud=latitud,
                    longitud=longitud,
                    direccion=direccion or '',
                    barrio=barrio or '',
                    ciudad=ciudad
                )
                db.session.add(ubicacion)
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def obtener_ubicacion(id: int) -> Tuple[Optional[Ubicacion], Optional[str]]:
        """Obtener ubicación de un vehículo"""
        try:
            ubicacion = Ubicacion.query.filter_by(vehiculo_id=id).first()
            if not ubicacion:
                return None, "El vehículo no tiene ubicación registrada"
            return ubicacion, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def buscar_por_ubicacion(latitud: float, longitud: float, radio_km: float = 5.0) -> List[Vehiculo]:
        """Buscar vehículos cerca de una ubicación"""
        # Fórmula Haversine aproximada para distancia en kilómetros
        # Esto es una aproximación simple, para producción considera usar PostGIS o similar
        query = """
        SELECT v.*, 
            (6371 * acos(
                cos(radians(:lat)) * cos(radians(u.latitud)) * 
                cos(radians(u.longitud) - radians(:lon)) + 
                sin(radians(:lat)) * sin(radians(u.latitud))
            )) as distancia_km
        FROM vehiculos v
        JOIN ubicaciones u ON v.id = u.vehiculo_id
        WHERE v.estado = 'disponible' 
            AND v.estado_ruta = 'disponible'
        HAVING distancia_km <= :radio
        ORDER BY distancia_km
        """
        
        try:
            resultados = db.session.execute(
                query, 
                {'lat': latitud, 'lon': longitud, 'radio': radio_km}
            ).fetchall()
            
            vehiculos = []
            for row in resultados:
                vehiculo_dict = dict(row)
                # Convertir a objeto Vehiculo si es necesario
                vehiculo = Vehiculo.query.get(vehiculo_dict['id'])
                if vehiculo:
                    setattr(vehiculo, 'distancia_km', vehiculo_dict['distancia_km'])
                    vehiculos.append(vehiculo)
            
            return vehiculos
        except Exception as e:
            print(f"Error en búsqueda por ubicación: {e}")
            return []
    
    @staticmethod
    def asignar_conductor(id: int, conductor_id: int) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Asignar conductor a un vehículo"""
        try:
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Aquí podrías agregar validación para verificar que el conductor existe
            # conductor = Conductor.query.get(conductor_id)
            # if not conductor:
            #     return None, "Conductor no encontrado"
            
            vehiculo.conductor_id = conductor_id
            vehiculo.updated_at = datetime.utcnow()
            
            db.session.commit()
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def desasignar_conductor(id: int) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Desasignar conductor de un vehículo"""
        try:
            vehiculo = Vehiculo.query.get(id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            vehiculo.conductor_id = None
            vehiculo.updated_at = datetime.utcnow()
            
            db.session.commit()
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)