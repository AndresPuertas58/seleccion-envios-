from app.models.envio import Envio
from app.models.punto_venta import PuntoVenta
from app import db
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class EnvioService:
    @staticmethod
    def get_all(include_punto_venta: bool = False) -> List[Envio]:
        """Obtener todos los envíos"""
        query = Envio.query.order_by(Envio.created_at.desc())
        
        if include_punto_venta:
            query = query.options(db.joinedload(Envio.punto_venta))
        
        return query.all()
    
    @staticmethod
    def get_by_id(id: int, include_punto_venta: bool = False) -> Optional[Envio]:
        """Obtener envío por ID"""
        query = Envio.query
        
        if include_punto_venta:
            query = query.options(db.joinedload(Envio.punto_venta))
        
        return query.get(id)
    
    @staticmethod
    def get_by_punto_venta(punto_venta_id: int) -> List[Envio]:
        """Obtener envíos por punto de venta"""
        return Envio.query.filter_by(punto_venta_id=punto_venta_id).order_by(Envio.created_at.desc()).all()
    
    @staticmethod
    def get_by_estado(estado: str) -> List[Envio]:
        """Obtener envíos por estado"""
        return Envio.query.filter_by(estado=estado).order_by(Envio.created_at.desc()).all()
    
    @staticmethod
    def create(data: Dict) -> Tuple[Optional[Envio], Optional[str]]:
        """Crear un nuevo envío"""
        try:
            # Validar campos requeridos
            campos_requeridos = ['punto_venta_id', 'tipo_carga', 'peso_carga', 'remitente', 'destino']
            for campo in campos_requeridos:
                if campo not in data:
                    return None, f"Campo requerido: {campo}"
            
            # Verificar que el punto de venta existe
            punto_venta = PuntoVenta.query.get(data['punto_venta_id'])
            if not punto_venta:
                return None, "Punto de venta no encontrado"
            
            # Validar peso
            try:
                peso = float(data['peso_carga'])
                if peso <= 0:
                    return None, "El peso debe ser mayor a 0"
            except (ValueError, TypeError):
                return None, "Peso inválido. Debe ser un número"
            
            # Validar fechas si están presentes
            fecha_estimada = None
            if 'fecha_estimada_entrega' in data and data['fecha_estimada_entrega']:
                try:
                    fecha_estimada = datetime.strptime(data['fecha_estimada_entrega'], '%Y-%m-%d').date()
                except ValueError:
                    return None, "Fecha estimada debe estar en formato YYYY-MM-DD"
            
            fecha_real = None
            if 'fecha_real_entrega' in data and data['fecha_real_entrega']:
                try:
                    fecha_real = datetime.strptime(data['fecha_real_entrega'], '%Y-%m-%d').date()
                except ValueError:
                    return None, "Fecha real debe estar en formato YYYY-MM-DD"
            
            # Crear envío
            envio = Envio(
                punto_venta_id=data['punto_venta_id'],
                tipo_carga=data['tipo_carga'],
                peso_carga=peso,
                remitente=data['remitente'],
                destino=data['destino'],
                estado=data.get('estado', 'pendiente'),
                fecha_estimada_entrega=fecha_estimada,
                fecha_real_entrega=fecha_real,
                observaciones=data.get('observaciones')
            )
            
            db.session.add(envio)
            db.session.commit()
            return envio, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)