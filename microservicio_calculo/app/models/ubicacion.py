from app import db
from datetime import datetime

class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id', ondelete='CASCADE'), nullable=False)
    latitud = db.Column(db.Numeric(10, 8), nullable=False)
    longitud = db.Column(db.Numeric(11, 8), nullable=False)
    direccion = db.Column(db.String(200))
    barrio = db.Column(db.String(100))
    ciudad = db.Column(db.String(50), default='Bogotá')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    vehiculo = db.relationship('Vehiculo', back_populates='ubicacion')
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehiculo_id': self.vehiculo_id,
            'latitud': float(self.latitud) if self.latitud else None,
            'longitud': float(self.longitud) if self.longitud else None,
            'direccion': self.direccion,
            'barrio': self.barrio,
            'ciudad': self.ciudad,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultima_actualizacion': self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None
        }