import requests
import random
import json

def sistema_camiones_simple():
    # Configuración
    GH_URL = "http://localhost:8989"
    ciudad = "bogota"  
    
    # Coordenadas de ejemplo en Bogotá
    bbox_bogota = {"min_lat": 4.48, "max_lat": 4.85, "min_lon": -74.25, "max_lon": -74.00}
    
  
    camiones = []
    for i in range(3):
        camion = {
            "id": f"CAM-{i+1}",
            "lat": round(random.uniform(bbox_bogota["min_lat"], bbox_bogota["max_lat"]), 6),
            "lon": round(random.uniform(bbox_bogota["min_lon"], bbox_bogota["max_lon"]), 6)
        }
        camiones.append(camion)
    
    destino = {"lat": 4.598056, "lon": -74.075833}
    
    print("🚚 CAMIONES GENERADOS:")
    for c in camiones:
        print(f"  {c['id']}: ({c['lat']}, {c['lon']})")
    
    print(f"\n🎯 DESTINO: ({destino['lat']}, {destino['lon']})")
    
    # Calcular rutas
    resultados = []
    for camion in camiones:
        url = f"{GH_URL}/route"
        params = {
            "point": [f"{camion['lat']},{camion['lon']}", 
                     f"{destino['lat']},{destino['lon']}"],
            "profile": "car"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data.get("paths"):
                ruta = data["paths"][0]
                resultados.append({
                    **camion,
                    "distancia_km": ruta["distance"] / 1000,
                    "tiempo_min": ruta["time"] / 60000
                })
        except:
            continue
    
    # Mostrar resultados
    if resultados:
        resultados.sort(key=lambda x: x["tiempo_min"])
        print("\n🏆 CAMIÓN MÁS CERCANO:")
        mejor = resultados[0]
        print(f"✅ {mejor['id']}")
        print(f"  📍 Ubicación: {mejor['lat']}, {mejor['lon']}")
        print(f"  📏 Distancia: {mejor['distancia_km']:.1f} km")
        print(f"  ⏱️  Tiempo: {mejor['tiempo_min']:.1f} min")
        
        # URL para ver en mapa
        url_mapa = f"{GH_URL}/maps/?point={mejor['lat']},{mejor['lon']}&point={destino['lat']},{destino['lon']}&profile=car"
        print(f"\n🌐 Ver ruta: {url_mapa}")
    else:
        print("\n❌ No se pudieron calcular rutas")

# Ejecutar
sistema_camiones_simple()