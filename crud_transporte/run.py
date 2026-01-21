#!/usr/bin/env python3
"""
🚀 Punto de entrada de la aplicación Sistema de Transporte
"""
import os
from app import create_app
from app.services.database_service import DatabaseService

# Crear aplicación
app = create_app()

if __name__ == '__main__':
    print("""
    🚀 API Sistema de Transporte - INICIANDO
    ============================================
    
    📍 Endpoints disponibles:
    
    VEHÍCULOS:
      GET     /api/vehiculos          - Listar todos
      GET     /api/vehiculos/<id>     - Obtener uno
      POST    /api/vehiculos          - Crear nuevo
      PUT     /api/vehiculos/<id>     - Actualizar
      DELETE  /api/vehiculos/<id>     - Eliminar
    
    CONDUCTORES:
      GET     /api/conductores        - Listar todos
      GET     /api/conductores/<id>   - Obtener uno
      POST    /api/conductores        - Crear nuevo
      PUT     /api/conductores/<id>   - Actualizar
      DELETE  /api/conductores/<id>   - Eliminar
    
    USUARIOS APP:
      GET     /api/usuarios           - Listar todos
      GET     /api/usuarios/<id>      - Obtener uno
      POST    /api/usuarios           - Crear nuevo
      PUT     /api/usuarios/<id>      - Actualizar
      DELETE  /api/usuarios/<id>      - Eliminar
      POST    /api/usuarios/login     - Login
      PUT     /api/usuarios/<id>/cambiar-password - Cambiar contraseña
    
    OTROS:
      GET     /api/estadisticas       - Estadísticas
      GET     /api/health             - Health check
      GET     /api/docs               - Documentación Swagger
    
    🌐 Servidor: http://localhost:5000
    📚 Documentación: http://localhost:5000/api/docs
    ============================================
    """)
    
    # Inicializar base de datos
    with app.app_context():
        success, error = DatabaseService.init_db()
        if not success:
            print(f"❌ Error al inicializar base de datos: {error}")
            print("\n🔧 SOLUCIÓN:")
            print("1. Verifica que MySQL esté corriendo: sudo systemctl status mysql")
            print("2. Verifica que la base de datos exista:")
            print("   mysql -u coltanques -p")
            print("   CREATE DATABASE IF NOT EXISTS sistema_transporte;")
            print("3. Verifica tu contraseña en el archivo .env")
        else:
            print("✅ Base de datos inicializada correctamente")
    
    # Iniciar servidor
    app.run(
        debug=app.config.get('DEBUG', True),
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000))
    )