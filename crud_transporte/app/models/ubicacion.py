# app/models/ubicacion.py
from app import db

class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'), nullable=False, unique=True)
    latitud = db.Column(db.DECIMAL(10, 8), nullable=False)
    longitud = db.Column(db.DECIMAL(11, 8), nullable=False)
    direccion = db.Column(db.String(200))
    barrio = db.Column(db.String(100))
    ciudad = db.Column(db.String(50), default='Bogotá')
    fecha_registro = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    ultima_actualizacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), 
                                    onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehiculo_id': self.vehiculo_id,
            'latitud': float(self.latitud) if self.latitud else None,
            'longitud': float(self.longitud) if self.longitud else None,
            'direccion': self.direccion,
            'barrio': self.barrio,
            'ciudad': self.ciudad
        }