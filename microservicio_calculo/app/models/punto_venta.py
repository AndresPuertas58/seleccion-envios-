from app import db
from datetime import datetime

class PuntoVenta(db.Model):
    __tablename__ = 'puntos_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False, default='Bogotá')
    latitud = db.Column(db.Numeric(10, 8), nullable=False)
    longitud = db.Column(db.Numeric(11, 8), nullable=False)
    barrio = db.Column(db.String(100))
    encargado = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    estado = db.Column(db.Enum('activo', 'inactivo', name='estados_punto_venta'), default='activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    envios = db.relationship('Envio', back_populates='punto_venta', cascade='all, delete-orphan')
    
    def to_dict(self, include_envios: bool = False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'ubicacion': self.ubicacion,
            'latitud': float(self.latitud) if self.latitud else None,
            'longitud': float(self.longitud) if self.longitud else None,
            'barrio': self.barrio,
            'encargado': self.encargado,
            'telefono': self.telefono,
            'email': self.email,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_envios:
            data['envios'] = [envio.to_dict() for envio in self.envios]
        
        return data