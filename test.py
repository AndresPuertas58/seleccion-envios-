# test_all_endpoints_5001.py
import requests
import json
import time

BASE_URL = "http://localhost:5001/api/calculo"

def print_response(response, title=""):
    """Función para imprimir respuestas de manera ordenada"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"📍 Endpoint: {response.url}")
    print(f"📊 Status: {response.status_code}")
    print(f"⏱️  Tiempo: {response.elapsed.total_seconds():.2f}s")
    
    try:
        data = response.json()
        print("\n📦 Respuesta JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Extraer información útil
        if 'total' in data:
            print(f"\n📊 Total registros: {data['total']}")
        if 'success' in data:
            print(f"✅ Success: {data['success']}")
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            
    except json.JSONDecodeError:
        print(f"\n📄 Respuesta texto: {response.text[:200]}...")
    
    return response.json() if response.text else {}

def test_get_endpoints():
    """Probar endpoints GET"""
    print("🚀 INICIANDO PRUEBAS DE ENDPOINTS GET")
    
    # 1. Envíos pendientes
    response = requests.get(f"{BASE_URL}/envios-pendientes")
    envios_data = print_response(response, "1. ENVÍOS PENDIENTES")
    
    # Guardar IDs para pruebas posteriores
    envio_id = None
    if envios_data.get('envios'):
        envio_id = envios_data['envios'][0]['envio']['id']
        print(f"\n📌 ID de envío encontrado: {envio_id}")
    
    # 2. Vehículos disponibles
    response = requests.get(f"{BASE_URL}/vehiculos-disponibles")
    vehiculos_data = print_response(response, "2. VEHÍCULOS DISPONIBLES")
    
    # Guardar ID de vehículo
    vehiculo_id = None
    if vehiculos_data.get('vehiculos'):
        vehiculo_id = vehiculos_data['vehiculos'][0]['id']
        print(f"\n📌 ID de vehículo encontrado: {vehiculo_id}")
    
    # 3. Encontrar mejor vehículo (si hay envío)
    if envio_id:
        response = requests.get(f"{BASE_URL}/encontrar-mejor-vehiculo/{envio_id}")
        print_response(response, f"3. MEJOR VEHÍCULO PARA ENVÍO {envio_id}")
    
    # 4. Reporte de envío (si hay envío)
    if envio_id:
        response = requests.get(f"{BASE_URL}/reporte-envio/{envio_id}")
        print_response(response, f"4. REPORTE DE ENVÍO {envio_id}")
    
    return envio_id, vehiculo_id

def test_post_endpoints(envio_id=None, vehiculo_id=None):
    """Probar endpoints POST"""
    print("\n\n🚀 INICIANDO PRUEBAS DE ENDPOINTS POST")
    
    # Datos de prueba para rutas (Bogotá -> Medellín)
    test_coords = {
        "origen_lat": 4.609710,    # Bogotá
        "origen_lng": -74.081749,
        "destino_lat": 6.244203,   # Medellín
        "destino_lng": -75.581215
    }
    
    # 5. Obtener ruta
    print("\n" + "="*60)
    print("5. OBTENER RUTA (Bogotá -> Medellín)")
    print("="*60)
    response = requests.post(f"{BASE_URL}/obtener-ruta", json=test_coords)
    ruta_data = print_response(response, "5. OBTENER RUTA")
    
    # Extraer puntos de ruta para peajes
    puntos_ruta = ruta_data.get('puntos_ruta', [])
    
    # 6. Calcular peajes (si hay puntos de ruta)
    if puntos_ruta and len(puntos_ruta) > 10:  # Si hay suficientes puntos
        print("\n" + "="*60)
        print("6. CALCULAR PEAJES")
        print("="*60)
        peajes_data = {
            "puntos_ruta": puntos_ruta[:50],  # Primeros 50 puntos para no sobrecargar
            "categoria": 1
        }
        response = requests.post(f"{BASE_URL}/calcular-peajes", json=peajes_data)
        print_response(response, "6. CALCULAR PEAJES")
    
    # 7. Simular envío
    print("\n" + "="*60)
    print("7. SIMULAR ENVÍO COMPLETO")
    print("="*60)
    simular_data = {
        **test_coords,
        "peso_kg": 500.0
    }
    response = requests.post(f"{BASE_URL}/simular-envio", json=simular_data)
    simular_result = print_response(response, "7. SIMULAR ENVÍO")
    
    # 8. Calcular envío específico (si tenemos IDs)
    if envio_id and vehiculo_id:
        print("\n" + "="*60)
        print(f"8. CALCULAR ENVÍO ESPECÍFICO (envio:{envio_id}, vehiculo:{vehiculo_id})")
        print("="*60)
        calcular_data = {
            "envio_id": envio_id,
            "vehiculo_id": vehiculo_id
        }
        response = requests.post(f"{BASE_URL}/calcular-envio", json=calcular_data)
        calcular_result = print_response(response, "8. CALCULAR ENVÍO ESPECÍFICO")
        
        # Si se creó un cálculo, guardar su ID
        calculo_id = None
        if calcular_result.get('success') and calcular_result.get('data'):
            calculo_id = calcular_result['data']['id']
            print(f"\n📌 Cálculo creado con ID: {calculo_id}")

def test_all_with_summary():
    """Ejecutar todas las pruebas con resumen"""
    print("🔧 CONFIGURACIÓN:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Puerto: 5001")
    print(f"   Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Probar conexión básica
        test_response = requests.get(f"{BASE_URL}/envios-pendientes", timeout=5)
        print(f"✅ Conexión exitosa al servidor")
        
        # Ejecutar pruebas
        start_time = time.time()
        
        envio_id, vehiculo_id = test_get_endpoints()
        test_post_endpoints(envio_id, vehiculo_id)
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ Todas las pruebas completadas en {elapsed_time:.1f} segundos")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: No se pudo conectar a {BASE_URL}")
        print("   Asegúrate de que el servidor Flask esté corriendo en puerto 5001")
        print("   Comando: flask run --port=5001")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_all_with_summary()