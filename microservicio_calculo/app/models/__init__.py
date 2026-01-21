from app.models.vehiculo import Vehiculo
from app.models.conductor import Conductor
from app.models.ubicacion import Ubicacion
from app.models.punto_venta import PuntoVenta
from app.models.envio import Envio
from app.models.envio_calculo import CalculoEnvio

# Lista de todos los modelos para db.create_all()
__all__ = [
    'Vehiculo',
    'Conductor',
    'Ubicacion',
    'PuntoVenta',
    'Envio',
    'CalculoEnvio'
]