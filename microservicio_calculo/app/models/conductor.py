from datetime import datetime
from app import db

class Conductor(db.Model):
    __tablename__ = 'conductores'
    
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    licencia = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    direccion = db.Column(db.Text)
    fecha_nacimiento = db.Column(db.Date)
    estado = db.Column(db.Enum('activo', 'inactivo', 'vacaciones', 'suspendido', name='estados_conductor'), default='activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones CORREGIDAS
    vehiculos = db.relationship('Vehiculo', back_populates='conductor')
    
    def to_dict(self, include_vehiculos: bool = False):
        data = {
            'id': self.id,
            'dni': self.dni,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'licencia': self.licencia,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_vehiculos:
            data['vehiculos'] = [vehiculo.to_dict() for vehiculo in self.vehiculos]
        
        return data