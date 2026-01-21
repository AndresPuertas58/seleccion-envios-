# app/models/destino.py
from app import db
from sqlalchemy import DECIMAL
from sqlalchemy.orm import relationship

class Destino(db.Model):
    __tablename__ = 'destinos'
    
    id = db.Column(db.Integer, primary_key=True)
    ciudad = db.Column(db.String(100), nullable=False, unique=True)
    latitud = db.Column(DECIMAL(10, 8), nullable=False)
    longitud = db.Column(DECIMAL(11, 8), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    
    # Relaciones
    # No hay relación directa con envío (por string) pero se puede inferir si fuera necesario
    # envios = relationship('Envio', secondary='envio_destinos', back_populates='destinos')
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'ciudad': self.ciudad,
            'latitud': float(self.latitud),
            'longitud': float(self.longitud)
        }
    
    def obtener_coordenadas(self):
        """Obtener coordenadas como tupla (lat, lng)"""
        return (float(self.latitud), float(self.longitud))