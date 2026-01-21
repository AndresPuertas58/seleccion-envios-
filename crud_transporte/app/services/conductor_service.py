from app.models.conductor import Conductor
from app import db
from datetime import datetime

class ConductorService:
    @staticmethod
    def get_all():
        return Conductor.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Conductor.query.get(id)
    
    @staticmethod
    def create(data):
        try:
            conductor = Conductor(
                dni=data['dni'],
                nombre=data['nombre'],
                apellido=data['apellido'],
                licencia=data.get('licencia', ''),
                telefono=data.get('telefono', ''),
                email=data.get('email', ''),
                direccion=data.get('direccion', ''),
                estado=data.get('estado', 'activo')
            )
            
            if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
                conductor.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d')
            
            db.session.add(conductor)
            db.session.commit()
            return conductor, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update(id, data):
        try:
            conductor = Conductor.query.get(id)
            if not conductor:
                return None, "Conductor no encontrado"
            
            campos = ['dni', 'nombre', 'apellido', 'licencia', 'telefono', 'email', 'direccion', 'estado']
            for campo in campos:
                if campo in data:
                    setattr(conductor, campo, data[campo])
            
            if 'fecha_nacimiento' in data:
                conductor.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data['fecha_nacimiento'] else None
            
            db.session.commit()
            return conductor, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete(id):
        try:
            conductor = Conductor.query.get(id)
            if not conductor:
                return False, "Conductor no encontrado"
            
            db.session.delete(conductor)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_estadisticas():
        return {
            'total': Conductor.query.count(),
            'activos': Conductor.query.filter_by(estado='activo').count(),
            'inactivos': Conductor.query.filter_by(estado='inactivo').count()
        }