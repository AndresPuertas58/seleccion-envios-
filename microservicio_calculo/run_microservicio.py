from app import create_app

# Crear la aplicación
app = create_app()

# Importar y registrar el blueprint ANTES de ejecutar
from app.controllers.calculo_controller import calculo_bp
app.register_blueprint(calculo_bp)

if __name__ == '__main__':
    print("=" * 60)
    print("🎯 MICROSERVICIO DE CÁLCULO DE ENVÍOS")
    print("=" * 60)
    print("✅ Blueprint registrado: /api/calculo")
    print(f"🌐 URL: http://localhost:5001")
    print("\n📋 Endpoints disponibles:")
    print("  GET  /api/calculo/health")
    print("  GET  /api/calculo/verificar-graphhopper")
    print("  GET  /api/calculo/test-ruta")
    print("  POST /api/calculo/simular-envio")
    print("  POST /api/calculo/calcular-ruta")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)