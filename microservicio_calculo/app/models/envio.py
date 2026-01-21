from app import db
from datetime import datetime

class Envio(db.Model):
    __tablename__ = 'envios'
    
    id = db.Column(db.Integer, primary_key=True)
    punto_venta_id = db.Column(db.Integer, db.ForeignKey('puntos_venta.id', ondelete='CASCADE'), nullable=False)
    tipo_carga = db.Column(db.String(50), nullable=False)
    peso_carga = db.Column(db.Numeric(10, 2), nullable=False)
    remitente = db.Column(db.String(150), nullable=False)
    destino = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.Enum('pendiente', 'en_transito', 'entregado', 'cancelado', name='estados_envio'), default='pendiente')
    fecha_estimada_entrega = db.Column(db.Date)
    fecha_real_entrega = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    punto_venta = db.relationship('PuntoVenta', back_populates='envios')
    calculos_envio = db.relationship('CalculoEnvio', backref='envio_relacion', cascade='all, delete-orphan')
    
    def to_dict(self, include_punto_venta: bool = False, include_calculos: bool = False):
        data = {
            'id': self.id,
            'punto_venta_id': self.punto_venta_id,
            'tipo_carga': self.tipo_carga,
            'peso_carga': float(self.peso_carga) if self.peso_carga else None,
            'remitente': self.remitente,
            'destino': self.destino,
            'estado': self.estado,
            'fecha_estimada_entrega': self.fecha_estimada_entrega.isoformat() if self.fecha_estimada_entrega else None,
            'fecha_real_entrega': self.fecha_real_entrega.isoformat() if self.fecha_real_entrega else None,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_punto_venta and self.punto_venta:
            data['punto_venta'] = self.punto_venta.to_dict()
        
        if include_calculos:
            data['calculos_envio'] = [calculo.to_dict() for calculo in self.calculos_envio]
        
        return data