from app.models.vehiculo import Vehiculo
from app.models.conductor import Conductor
from app import db
from datetime import datetime
from typing import Tuple, Optional

class AsignacionService:
    @staticmethod
    def asignar_conductor_vehiculo(vehiculo_id: int, conductor_id: int) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Asignar un conductor a un vehículo"""
        try:
            # Verificar que el vehículo existe
            vehiculo = Vehiculo.query.get(vehiculo_id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Verificar que el conductor existe
            conductor = Conductor.query.get(conductor_id)
            if not conductor:
                return None, "Conductor no encontrado"
            
            # Verificar que el vehículo esté disponible
            if vehiculo.estado != 'disponible':
                return None, f"Vehículo no disponible. Estado actual: {vehiculo.estado}"
            
            # Verificar que el conductor no tenga otro vehículo asignado
            if conductor.vehiculo:
                return None, f"Conductor ya tiene asignado el vehículo con ID: {conductor.vehiculo.id}"
            
            # Verificar que el vehículo no tenga otro conductor
            if vehiculo.conductor:
                return None, f"Vehículo ya tiene asignado el conductor: {vehiculo.conductor.nombre}"
            
            # Asignar conductor al vehículo
            vehiculo.conductor_id = conductor_id
            vehiculo.estado = 'en_uso'  # Cambiar estado a en uso
            vehiculo.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def desasignar_conductor_vehiculo(vehiculo_id: int) -> Tuple[Optional[Vehiculo], Optional[str]]:
        """Desasignar conductor de un vehículo"""
        try:
            # Verificar que el vehículo existe
            vehiculo = Vehiculo.query.get(vehiculo_id)
            if not vehiculo:
                return None, "Vehículo no encontrado"
            
            # Verificar que tenga conductor asignado
            if not vehiculo.conductor:
                return None, "Este vehículo no tiene conductor asignado"
            
            # Desasignar
            vehiculo.conductor_id = None
            vehiculo.estado = 'disponible'  # Cambiar estado a disponible
            vehiculo.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return vehiculo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_vehiculos_con_conductor():
        """Obtener vehículos con conductor asignado"""
        return Vehiculo.query.filter(Vehiculo.conductor_id.isnot(None)).all()
    
    @staticmethod
    def get_vehiculos_sin_conductor():
        """Obtener vehículos sin conductor asignado"""
        return Vehiculo.query.filter(
            Vehiculo.conductor_id.is_(None),
            Vehiculo.estado == 'disponible'
        ).all()
    
    @staticmethod
    def get_conductores_disponibles():
        """Obtener conductores disponibles para asignar"""
        # Conductores sin vehículo asignado
        return Conductor.query.filter(
            Conductor.estado == 'activo',
            ~Conductor.id.in_(
                db.session.query(Vehiculo.conductor_id).filter(Vehiculo.conductor_id.isnot(None))
            )
        ).all()