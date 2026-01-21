def validate_email(email):
    """Validar formato de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_dni(dni):
    """Validar formato de DNI (ejemplo para Perú)"""
    import re
    pattern = r'^\d{8}$'
    return bool(re.match(pattern, dni))

def validate_phone(phone):
    """Validar formato de teléfono"""
    import re
    pattern = r'^[\d\s\-\+\(\)]{7,15}$'
    return bool(re.match(pattern, phone))