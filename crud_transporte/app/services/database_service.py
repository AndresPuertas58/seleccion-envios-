from app import db
from app.models.vehiculo import Vehiculo
from app.models.conductor import Conductor
from app.models.usuario import UsuarioApp

class DatabaseService:
    @staticmethod
    def init_db():
        """Crear todas las tablas"""
        try:
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def health_check():
        """Verificar estado de la base de datos"""
        try:
            db.session.execute('SELECT 1')
            return True, "Base de datos conectada"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_estadisticas_generales():
        """Obtener estadísticas generales del sistema"""
        try:
            return {
                'vehiculos': {
                    'total': Vehiculo.query.count(),
                    'disponibles': Vehiculo.query.filter_by(estado='disponible').count(),
                    'en_uso': Vehiculo.query.filter_by(estado='en_uso').count(),
                    'mantenimiento': Vehiculo.query.filter_by(estado='mantenimiento').count()
                },
                'conductores': {
                    'total': Conductor.query.count(),
                    'activos': Conductor.query.filter_by(estado='activo').count(),
                    'inactivos': Conductor.query.filter_by(estado='inactivo').count()
                },
                'usuarios': {
                    'total': UsuarioApp.query.count(),
                    'activos': UsuarioApp.query.filter_by(activo=True).count(),
                    'inactivos': UsuarioApp.query.filter_by(activo=False).count()
                }
            }
        except Exception as e:
            return None