from app.models.usuario import UsuarioApp
from app import db
from datetime import datetime

class UsuarioService:
    @staticmethod
    def get_all():
        return UsuarioApp.query.all()
    
    @staticmethod
    def get_by_id(id):
        return UsuarioApp.query.get(id)
    
    @staticmethod
    def get_by_username(username):
        return UsuarioApp.query.filter_by(username=username).first()
    
    @staticmethod
    def create(data):
        try:
            # Validar existencia
            if UsuarioApp.query.filter_by(username=data['username']).first():
                return None, "El nombre de usuario ya existe"
            
            if UsuarioApp.query.filter_by(email=data['email']).first():
                return None, "El email ya está registrado"
            
            usuario = UsuarioApp(
                username=data['username'],
                email=data['email'],
                nombre=data['nombre'],
                telefono=data.get('telefono', ''),
                activo=data.get('activo', True)
            )
            
            usuario.set_password(data['password'])
            db.session.add(usuario)
            db.session.commit()
            return usuario, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update(id, data):
        try:
            usuario = UsuarioApp.query.get(id)
            if not usuario:
                return None, "Usuario no encontrado"
            
            # Actualizar username
            if 'username' in data and data['username'] != usuario.username:
                if UsuarioApp.query.filter_by(username=data['username']).first():
                    return None, "El nombre de usuario ya existe"
                usuario.username = data['username']
            
            # Actualizar email
            if 'email' in data and data['email'] != usuario.email:
                if UsuarioApp.query.filter_by(email=data['email']).first():
                    return None, "El email ya está registrado"
                usuario.email = data['email']
            
            # Actualizar otros campos
            if 'nombre' in data:
                usuario.nombre = data['nombre']
            
            if 'telefono' in data:
                usuario.telefono = data['telefono']
            
            if 'activo' in data:
                usuario.activo = bool(data['activo'])
            
            # Actualizar contraseña
            if 'password' in data and data['password']:
                usuario.set_password(data['password'])
            
            db.session.commit()
            return usuario, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete(id):
        try:
            usuario = UsuarioApp.query.get(id)
            if not usuario:
                return False, "Usuario no encontrado"
            
            db.session.delete(usuario)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def authenticate(username, password):
        usuario = UsuarioApp.query.filter_by(username=username).first()
        if not usuario or not usuario.check_password(password):
            return None, "Credenciales incorrectas"
        
        if not usuario.activo:
            return None, "Usuario inactivo"
        
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        return usuario, None
    
    @staticmethod
    def cambiar_password(id, current_password, new_password):
        try:
            usuario = UsuarioApp.query.get(id)
            if not usuario:
                return False, "Usuario no encontrado"
            
            if not usuario.check_password(current_password):
                return False, "Contraseña actual incorrecta"
            
            usuario.set_password(new_password)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_estadisticas():
        return {
            'total': UsuarioApp.query.count(),
            'activos': UsuarioApp.query.filter_by(activo=True).count(),
            'inactivos': UsuarioApp.query.filter_by(activo=False).count()
        }