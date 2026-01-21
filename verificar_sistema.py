# test_verificar.py
import sys
sys.path.append('.')
from app.services.calculo_service import CalculoEnvioService

servicio = CalculoEnvioService()

# Lista de métodos que deberían existir
metodos_requeridos = [
    'buscar_envios_pendientes',
    'buscar_vehiculos_disponibles', 
    'calcular_envio',
    'simular_envio',  # ¡Este es el que falta!
    'encontrar_mejor_vehiculo',
    'generar_reporte_envio'
]

print("🔍 Verificando métodos de CalculoEnvioService:")
print("-" * 40)

for metodo in metodos_requeridos:
    tiene_metodo = hasattr(servicio, metodo)
    icono = "✅" if tiene_metodo else "❌"
    print(f"{icono} {metodo}: {tiene_metodo}")

if hasattr(servicio, 'simular_envio'):
    print("\n🎉 ¡El método simular_envio está disponible!")
    print("   Reinicia Flask y prueba el endpoint nuevamente.")
else:
    print("\n⚠️  El método simular_envio NO está disponible.")
    print("   Agrégalo a calculo_service.py como se indicó.")