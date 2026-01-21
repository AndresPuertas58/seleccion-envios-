from app import db
from datetime import datetime

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('camion', 'auto', name='tipos_vehiculo'), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(100), nullable=False)
    codigo_serial = db.Column(db.String(100), unique=True)
    placa = db.Column(db.String(20), unique=True)
    color = db.Column(db.String(30))
    estado = db.Column(db.Enum('disponible', 'en_uso', 'mantenimiento', 'desactivado', name='estados_vehiculo'), default='disponible')
    fecha_adquisicion = db.Column(db.Date)
    ultimo_mantenimiento = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id', ondelete='SET NULL'))
    estado_ruta = db.Column(db.Enum('disponible', 'en_ruta', 'cargando', 'mantenimiento', name='estados_ruta'), default='disponible')
    
    # Relaciones CORREGIDAS
    ubicacion = db.relationship('Ubicacion', back_populates='vehiculo', uselist=False, cascade='all, delete-orphan')
    conductor = db.relationship('Conductor', back_populates='vehiculos')
    
    def to_dict(self, include_ubicacion: bool = False, include_conductor: bool = False):
        data = {
            'id': self.id,
            'tipo': self.tipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'codigo_serial': self.codigo_serial,
            'placa': self.placa,
            'color': self.color,
            'estado': self.estado,
            'estado_ruta': self.estado_ruta,
            'fecha_adquisicion': self.fecha_adquisicion.isoformat() if self.fecha_adquisicion else None,
            'ultimo_mantenimiento': self.ultimo_mantenimiento.isoformat() if self.ultimo_mantenimiento else None,
            'conductor_id': self.conductor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_ubicacion and self.ubicacion:
            data['ubicacion'] = self.ubicacion.to_dict()
        
        if include_conductor and self.conductor:
            data['conductor'] = self.conductor.to_dict()
        
        return data