# probar_endpoints.py
import requests
import json

def probar_endpoint(method, url, data=None):
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            return {'error': 'Método no válido'}
        
        return {
            'status': response.status_code,
            'data': response.json() if response.headers.get('content-type') == 'application/json' else response.text
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    base_url = "http://localhost:5001/api/calculo"
    
    print("🚀 PROBANDO ENDPOINTS DEL MICROSERVICIO")
    print("=" * 60)
    
    # 1. Envíos pendientes
    print("\n1. 📋 GET /envios-pendientes")
    result = probar_endpoint('GET', f"{base_url}/envios-pendientes")
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 200:
        data = result.get('data', {})
        print(f"   Total envíos: {data.get('total', 0)}")
    else:
        print(f"   Error: {result.get('data', result.get('error', 'Desconocido'))}")
    
    # 2. Vehículos disponibles
    print("\n2. 🚚 GET /vehiculos-disponibles")
    result = probar_endpoint('GET', f"{base_url}/vehiculos-disponibles")
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 200:
        data = result.get('data', {})
        print(f"   Total vehículos: {data.get('total', 0)}")
        if data.get('vehiculos') and len(data['vehiculos']) > 0:
            print(f"   Primer vehículo: {data['vehiculos'][0].get('placa', 'Sin placa')}")
    else:
        print(f"   Error: {result.get('data', result.get('error', 'Desconocido'))}")
    
    # 3. Reporte de envío (ID 1)
    print("\n3. 📄 GET /reporte-envio/1")
    result = probar_endpoint('GET', f"{base_url}/reporte-envio/1")
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 200:
        data = result.get('data', {})
        if 'error' in data:
            print(f"   Error en datos: {data.get('error')}")
        else:
            print(f"   Envío ID: {data.get('envio', {}).get('id', 'N/A')}")
    else:
        print(f"   Error: {result.get('data', result.get('error', 'Desconocido'))}")
    
    # 4. Encontrar mejor vehículo (ID 1)
    print("\n4. 🔍 GET /encontrar-mejor-vehiculo/1")
    result = probar_endpoint('GET', f"{base_url}/encontrar-mejor-vehiculo/1")
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 200:
        data = result.get('data', {})
        print(f"   Total propuestas: {data.get('total_propuestas', 0)}")
    else:
        print(f"   Error: {result.get('data', result.get('error', 'Desconocido'))}")
    
    # 5. Simulación simple (sin Graphhopper)
    print("\n5. 📊 POST /simular-envio (versión simple)")
    payload = {
        "origen_lat": 4.609710,
        "origen_lng": -74.081749,
        "destino_lat": 4.6830486,
        "destino_lng": -74.0956113,
        "peso_kg": 1000
    }
    result = probar_endpoint('POST', f"{base_url}/simular-envio", payload)
    print(f"   Status: {result.get('status')}")
    if result.get('status') == 200:
        data = result.get('data', {})
        if 'error' in data:
            print(f"   Error Graphhopper: {data.get('error')}")
        else:
            sim = data.get('simulacion', {})
            print(f"   Distancia: {sim.get('distancia_km', 0):.2f} km")
    else:
        error_msg = result.get('data', result.get('error', 'Desconocido'))
        if isinstance(error_msg, dict) and 'error' in error_msg:
            print(f"   Error: {error_msg['error']}")
        else:
            print(f"   Error: {error_msg}")
    
    print("\n" + "=" * 60)
    print("💡 DIAGNÓSTICO:")
    print("- Si todos devuelven 404: El blueprint no está registrado")
    print("- Si devuelven 500: Error en modelos SQLAlchemy")
    print("- Si devuelven 200 pero sin datos: No hay datos en BD")
    print("- Si simular-envio da error 401: Graphhopper mal configurado")

if __name__ == "__main__":
    main()