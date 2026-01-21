# app/models/peaje.py
from app import db
from sqlalchemy import DECIMAL

class Peaje(db.Model):
    __tablename__ = 'peajes'
    
    id = db.Column(db.Integer, primary_key=True)
    X = db.Column(db.String(17))
    Y = db.Column(db.String(16))
    objectid = db.Column(db.Integer)
    codigotramo = db.Column(db.String(8))
    postereferencia = db.Column(db.Integer)
    distanciaposte = db.Column(db.Integer)
    nombrepeaje = db.Column(db.String(26))
    latitud = db.Column(DECIMAL(10, 8))
    longitud = db.Column(DECIMAL(11, 8))
    categoriai = db.Column(db.Integer)      # Categoría 1
    categoriaii = db.Column(db.Integer)     # Categoría 2
    categoriaiii = db.Column(db.String(5))  # Categoría 3 (string por si hay valores como 'N/A')
    categoriaiv = db.Column(db.Integer)     # Categoría 4
    categoriav = db.Column(db.Integer)      # Categoría 5
    categoriavi = db.Column(db.Integer)     # Categoría 6
    categoriavii = db.Column(db.Integer)    # Categoría 7
    linkfoto = db.Column(db.String(70))
    sector = db.Column(db.String(70))
    responsable = db.Column(db.String(50))
    sentido = db.Column(db.String(99))
    ubicacion = db.Column(db.String(121))
    telefonopeaje = db.Column(db.String(93))
    telefonogrua = db.Column(db.String(161))
    ejeadicional = db.Column(db.String(5))
    ejeadicionalr = db.Column(db.String(5))
    ejegrua = db.Column(db.String(5))
    
    # Métodos auxiliares
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombrepeaje,
            'lat': float(self.latitud) if self.latitud else None,
            'lng': float(self.longitud) if self.longitud else None,
            'costo_categoria_1': self.categoriai or 0,
            'costo_categoria_2': self.categoriaii or 0,
            'costo_categoria_3': int(self.categoriaiii) if self.categoriaiii and self.categoriaiii.isdigit() else 0,
            'costo_categoria_4': self.categoriaiv or 0,
            'costo_categoria_5': self.categoriav or 0,
            'ubicacion': self.ubicacion,
            'sector': self.sector,
            'responsable': self.responsable
        }
    
    def get_precio_categoria(self, categoria: int) -> float:
        """Obtener precio para una categoría específica"""
        precios = {
            1: self.categoriai or 0,
            2: self.categoriaii or 0,
            3: int(self.categoriaiii) if self.categoriaiii and self.categoriaiii.isdigit() else 0,
            4: self.categoriaiv or 0,
            5: self.categoriav or 0
        }
        return precios.get(categoria, 0)