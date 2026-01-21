# app/models/vehiculo.py
from app import db
from sqlalchemy.orm import relationship

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('camion', 'auto'), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(100), nullable=False)
    codigo_serial = db.Column(db.String(100), unique=True)
    placa = db.Column(db.String(20), unique=True)
    color = db.Column(db.String(30))
    estado = db.Column(db.Enum('disponible', 'en_uso', 'mantenimiento', 'desactivado'), 
                      default='disponible')
    estado_ruta = db.Column(db.Enum('disponible', 'en_ruta', 'cargando', 'mantenimiento'),
                           default='disponible')
    fecha_adquisicion = db.Column(db.Date)
    ultimo_mantenimiento = db.Column(db.Date)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'))
    
    # Relaciones
    conductor = relationship('Conductor', backref='vehiculos')
    ubicacion = relationship('Ubicacion', backref='vehiculo', uselist=False)
    
    def to_dict(self, include_conductor=False, include_ubicacion=False):
        """Convertir a diccionario con opciones"""
        data = {
            'id': self.id,
            'tipo': self.tipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'placa': self.placa,
            'color': self.color,
            'estado': self.estado,
            'estado_ruta': self.estado_ruta,
            'capacidad_kg': self._obtener_capacidad_por_tipo(),
            'conductor_id': self.conductor_id
        }
        
        if include_conductor and self.conductor:
            data['conductor'] = self.conductor.to_dict()
        
        if include_ubicacion and self.ubicacion:
            data['ubicacion_lat'] = float(self.ubicacion.latitud) if self.ubicacion.latitud else None
            data['ubicacion_lng'] = float(self.ubicacion.longitud) if self.ubicacion.longitud else None
            data['ubicacion_completa'] = {
                'direccion': self.ubicacion.direccion,
                'barrio': self.ubicacion.barrio,
                'ciudad': self.ubicacion.ciudad
            }
        
        return data
    
    def _obtener_capacidad_por_tipo(self):
        """Obtener capacidad según tipo de vehículo"""
        capacidades = {
            'camion': 10000,  # 10 toneladas
            'auto': 500       # 500 kg
        }
        return capacidades.get(self.tipo, 0)