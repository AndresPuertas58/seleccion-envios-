#!/usr/bin/env python3
"""
Sistema simple de asignación de camiones con coordenadas editables
"""

import requests
import json
from typing import Dict, List

# ================= CONFIGURACIÓN - EDITA AQUÍ =================
# 1. CONFIGURA TUS CAMIONES AQUÍ (lat, lon, capacidad)
CAMIONES_PERSONALIZADOS = [
    # Formato: [id, lat, lon, ciudad, capacidad(ton), estado]
    ["CAM-001", 4.615, -74.184, "Bosa-Bogotá", 10, "disponible"],
    ["CAM-002", 4.698, -74.083, "Suba-Bogotá", 15, "disponible"],
    ["CAM-003", 4.609, -74.081, "Centro-Bogotá", 5, "disponible"],
    # Agrega más camiones aquí:
    # ["CAM-004", 4.628, -74.064, "Chapinero", 8, "disponible"],
]

# 2. CONFIGURA TU DESTINO AQUÍ
DESTINO = {
    "lat": 4.598056,  # Plaza Bolívar Bogotá
    "lon": -74.075833,
    "nombre": "Plaza Bolívar"
}

# 3. CONFIGURACIÓN GRAPHHOPPER
GRAPHHOPPER_URL = "http://localhost:8989"
VEHICULO = "car"  # "car", "bike", "foot"

# ==============================================================

class SistemaCamionesSimple:
    def __init__(self):
        self.camiones = []
        self.cargar_camiones()
    
    def cargar_camiones(self):
        """Carga los camiones desde la configuración"""
        for camion_data in CAMIONES_PERSONALIZADOS:
            camion = {
                "id": camion_data[0],
                "lat": camion_data[1],
                "lon": camion_data[2],
                "ciudad": camion_data[3],
                "capacidad": camion_data[4],
                "estado": camion_data[5]
            }
            self.camiones.append(camion)
    
    def calcular_ruta(self, origen_lat: float, origen_lon: float, 
                     destino_lat: float, destino_lon: float) -> Dict:
        """Calcula ruta usando GraphHopper"""
        url = f"{GRAPHHOPPER_URL}/route"
        params = {
            "point": [f"{origen_lat},{origen_lon}", f"{destino_lat},{destino_lon}"],
            "profile": VEHICULO,
            "points_encoded": "false",
            "instructions": "false"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("paths") and len(data["paths"]) > 0:
                    ruta = data["paths"][0]
                    return {
                        "distancia_km": round(ruta["distance"] / 1000, 2),
                        "tiempo_min": round(ruta["time"] / 60000, 1),
                        "ascenso": ruta.get("ascend", 0),
                        "descenso": ruta.get("descend", 0),
                        "exito": True
                    }
        except Exception as e:
            print(f"Error calculando ruta: {e}")
        
        return {"distancia_km": None, "tiempo_min": None, "exito": False}
    
    def ejecutar(self):
        """Ejecuta el sistema completo"""
        print("=" * 60)
        print("🚚 SISTEMA DE ASIGNACIÓN DE CAMIONES - BOGOTÁ")
        print("=" * 60)
        
        # Mostrar camiones configurados
        print("\n📋 CAMIONES CONFIGURADOS:")
        for i, camion in enumerate(self.camiones, 1):
            print(f"  {i}. {camion['id']} - {camion['ciudad']}")
            print(f"     📍 ({camion['lat']}, {camion['lon']})")
            print(f"     ⚖️  {camion['capacidad']}T | 📊 {camion['estado']}")
        
        # Mostrar destino
        print(f"\n🎯 DESTINO: {DESTINO['nombre']}")
        print(f"   📍 ({DESTINO['lat']}, {DESTINO['lon']})")
        
        print("\n" + "=" * 60)
        print("🔍 CALCULANDO RUTAS...")
        print("=" * 60)
        
        # Calcular rutas para cada camión
        resultados = []
        
        for camion in self.camiones:
            print(f"\n🚚 {camion['id']} - {camion['ciudad']}")
            print(f"   Desde: ({camion['lat']}, {camion['lon']})")
            
            ruta = self.calcular_ruta(
                camion["lat"], camion["lon"],
                DESTINO["lat"], DESTINO["lon"]
            )
            
            if ruta["exito"]:
                camion_resultado = {
                    **camion,
                    "distancia_km": ruta["distancia_km"],
                    "tiempo_min": ruta["tiempo_min"]
                }
                resultados.append(camion_resultado)
                
                print(f"   ✅ RUTA CALCULADA")
                print(f"   📏 Distancia: {ruta['distancia_km']} km")
                print(f"   ⏱️  Tiempo: {ruta['tiempo_min']} min")
            else:
                print(f"   ❌ NO SE PUDO CALCULAR RUTA")
        
        # Mostrar resultados
        if resultados:
            # Ordenar por tiempo más rápido
            resultados.sort(key=lambda x: x["tiempo_min"])
            
            print("\n" + "=" * 60)
            print("🏆 RESULTADOS - ORDENADOS POR TIEMPO")
            print("=" * 60)
            
            for i, resultado in enumerate(resultados, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                print(f"\n{emoji} {i}. {resultado['id']} - {resultado['ciudad']}")
                print(f"   ⏱️  Tiempo: {resultado['tiempo_min']} min")
                print(f"   📏 Distancia: {resultado['distancia_km']} km")
                print(f"   ⚖️  Capacidad: {resultado['capacidad']}T")
                print(f"   📊 Estado: {resultado['estado']}")
            
            # Camión recomendado
            mejor = resultados[0]
            print("\n" + "=" * 60)
            print("✅ CAMIÓN RECOMENDADO PARA ASIGNAR")
            print("=" * 60)
            print(f"\n🚛 {mejor['id']} - {mejor['ciudad']}")
            print(f"📍 Ubicación: ({mejor['lat']}, {mejor['lon']})")
            print(f"⏱️  Llegará en: {mejor['tiempo_min']} minutos")
            print(f"📏 Distancia: {mejor['distancia_km']} km")
            print(f"⚖️  Capacidad: {mejor['capacidad']} toneladas")
            
            # Generar URL para ver en mapa
            url_mapa = (
                f"{GRAPHHOPPER_URL}/maps/?"
                f"point={mejor['lat']},{mejor['lon']}&"
                f"point={DESTINO['lat']},{DESTINO['lon']}&"
                f"profile={VEHICULO}"
            )
            print(f"\n🗺️  VER RUTA EN MAPA:")
            print(f"   {url_mapa}")
            
            # Guardar resultados en archivo
            self.guardar_resultados(mejor, resultados)
        else:
            print("\n❌ No se pudieron calcular rutas para ningún camión")
    
    def guardar_resultados(self, mejor: Dict, todos: List[Dict]):
        """Guarda los resultados en un archivo JSON"""
        resultado_final = {
            "destino": DESTINO,
            "camion_recomendado": mejor,
            "todos_camiones": todos,
            "fecha": json.dumps(str, default=str)  # Fecha actual
        }
        
        archivo = "resultado_asignacion.json"
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {archivo}")

def verificar_graphhopper():
    """Verifica que GraphHopper esté funcionando"""
    try:
        response = requests.get(f"{GRAPHHOPPER_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Verificando conexión con GraphHopper...")
    
    if verificar_graphhopper():
        print("✅ GraphHopper está funcionando en", GRAPHHOPPER_URL)
        print("   Vehículo configurado:", VEHICULO)
        
        sistema = SistemaCamionesSimple()
        sistema.ejecutar()
    else:
        print(f"❌ ERROR: GraphHopper no responde en {GRAPHHOPPER_URL}")
        print("   Asegúrate de tenerlo corriendo con:")
        print("   java -jar graphhopper-web-*.jar server config.yml")