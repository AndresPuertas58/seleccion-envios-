from app import db
from datetime import datetime

class CalculoEnvio(db.Model):
    __tablename__ = 'calculos_envio'
    
    id = db.Column(db.Integer, primary_key=True)
    envio_id = db.Column(db.Integer, db.ForeignKey('envios.id'))
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'))
    
    # Rutas y distancias
    ruta_json = db.Column(db.Text)
    distancia_km = db.Column(db.Numeric(10, 2))
    tiempo_minutos = db.Column(db.Numeric(10, 2))
    
    # Costos
    costo_combustible = db.Column(db.Numeric(10, 2))
    costo_peajes = db.Column(db.Numeric(10, 2))
    costo_total = db.Column(db.Numeric(10, 2))
    
    # Parámetros de cálculo
    precio_galon = db.Column(db.Numeric(10, 2))
    rendimiento_km_galon = db.Column(db.Numeric(10, 2))
    
    # Coordenadas
    origen_lat = db.Column(db.Numeric(10, 8))
    origen_lng = db.Column(db.Numeric(11, 8))
    destino_lat = db.Column(db.Numeric(10, 8))
    destino_lng = db.Column(db.Numeric(11, 8))
    
    estado = db.Column(db.Enum('pendiente', 'calculado', 'asignado', 'rechazado', name='estados_calculo'), default='calculado')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones CORREGIDAS
    envio = db.relationship('Envio', backref='calculos_asociados')  # Cambiado el backref
    vehiculo = db.relationship('Vehiculo')
    conductor = db.relationship('Conductor')
    
    def to_dict(self):
        import json
        
        data = {
            'id': self.id,
            'envio_id': self.envio_id,
            'vehiculo_id': self.vehiculo_id,
            'conductor_id': self.conductor_id,
            'distancia_km': float(self.distancia_km) if self.distancia_km else None,
            'tiempo_minutos': float(self.tiempo_minutos) if self.tiempo_minutos else None,
            'costo_combustible': float(self.costo_combustible) if self.costo_combustible else None,
            'costo_peajes': float(self.costo_peajes) if self.costo_peajes else None,
            'costo_total': float(self.costo_total) if self.costo_total else None,
            'precio_galon': float(self.precio_galon) if self.precio_galon else None,
            'rendimiento_km_galon': float(self.rendimiento_km_galon) if self.rendimiento_km_galon else None,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if self.ruta_json:
            try:
                data['ruta'] = json.loads(self.ruta_json)
            except:
                data['ruta'] = None
        
        if self.origen_lat and self.origen_lng:
            data['coordenadas_origen'] = {
                'lat': float(self.origen_lat),
                'lng': float(self.origen_lng)
            }
        
        if self.destino_lat and self.destino_lng:
            data['coordenadas_destino'] = {
                'lat': float(self.destino_lat),
                'lng': float(self.destino_lng)
            }
        
        if self.vehiculo:
            data['vehiculo'] = self.vehiculo.to_dict()
        
        if self.conductor:
            data['conductor'] = self.conductor.to_dict()
        
        if self.envio:
            data['envio'] = self.envio.to_dict()
        
        return data