# auth.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime, timedelta
from email_service import EmailService

class AuthSystem:
    def __init__(self):
        self.email_service = EmailService()
        self.sheet = self._connect_to_sheets()
        
    def _connect_to_sheets(self):
        """Conecta a Google Sheets para la autenticación"""
        try:
            # Intentar obtener credenciales de st.secrets (Streamlit Cloud)
            if 'google' in st.secrets:
                credentials = st.secrets['google']
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(credentials, scopes=scope)
                client = gspread.authorize(creds)
            else:
                # Para desarrollo local
                creds_dict = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS'))
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                client = gspread.authorize(creds)
            
            # Abrir o crear la hoja de usuarios
            try:
                spreadsheet = client.open('Almacen_Usuarios')
            except:
                spreadsheet = client.create('Almacen_Usuarios')
                # Compartir con tu correo para acceso
                spreadsheet.share(os.getenv('EMAIL_FROM'), perm_type='user', role='writer')
            
            # Obtener o crear la hoja de usuarios
            try:
                worksheet = spreadsheet.worksheet('Usuarios')
            except:
                worksheet = spreadsheet.add_worksheet('Usuarios', rows=1, cols=10)
                worksheet.append_row(['Email', 'Nombre', 'Contraseña', 'Rol', 'Verificado', 'Fecha_Registro', 'Codigo_Verificacion', 'Codigo_Expiracion', 'Activo'])
            
            return worksheet
            
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None
    
    def register_user(self, email, nombre, password, verification_code):
        """Registra un nuevo usuario con código de verificación"""
        if not self.sheet:
            return False, "Error de conexión a la base de datos"
        
        # Verificar que el email no exista
        existing_users = self.sheet.get_all_records()
        for user in existing_users:
            if user.get('Email') == email:
                return False, "Este email ya está registrado"
        
        # Encriptar contraseña
        hashed_password = self.email_service.hash_password(password)
        
        # Fecha de expiración del código (10 minutos)
        expiry_time = datetime.now() + timedelta(minutes=10)
        
        # Agregar usuario
        try:
            self.sheet.append_row([
                email,
                nombre,
                hashed_password,
                'user',  # Rol por defecto
                False,   # No verificado
                datetime.now().isoformat(),
                verification_code,
                expiry_time.isoformat(),
                True     # Activo
            ])
            return True, "Usuario registrado correctamente"
        except Exception as e:
            return False, f"Error al registrar: {e}"
    
    def verify_user_code(self, email, code):
        """Verifica el código de confirmación"""
        if not self.sheet:
            return False, "Error de conexión"
        
        users = self.sheet.get_all_records()
        for idx, user in enumerate(users, start=2):  # start=2 porque la fila 1 es encabezado
            if user.get('Email') == email:
                stored_code = user.get('Codigo_Verificacion')
                expiry = user.get('Codigo_Expiracion')
                
                if not stored_code or not expiry:
                    return False, "Código no encontrado"
                
                # Verificar expiración
                expiry_time = datetime.fromisoformat(expiry)
                if datetime.now() > expiry_time:
                    return False, "El código ha expirado"
                
                if stored_code == code:
                    # Marcar como verificado
                    self.sheet.update(f'F{idx}', 'True')
                    return True, "Cuenta verificada exitosamente"
                else:
                    return False, "Código incorrecto"
        
        return False, "Email no encontrado"
    
    def login(self, email, password):
        """Inicia sesión de usuario"""
        if not self.sheet:
            return None, "Error de conexión"
        
        users = self.sheet.get_all_records()
        for user in users:
            if user.get('Email') == email:
                # Verificar si está activo
                if not user.get('Activo', True):
                    return None, "Cuenta desactivada"
                
                # Verificar si está verificado
                if not user.get('Verificado', False):
                    return None, "Cuenta no verificada. Por favor, verifica tu correo"
                
                # Verificar contraseña
                if self.email_service.verify_password(password, user.get('Contraseña')):
                    return {
                        'email': user.get('Email'),
                        'nombre': user.get('Nombre'),
                        'rol': user.get('Rol', 'user'),
                        'verificado': user.get('Verificado', False)
                    }, "Login exitoso"
                else:
                    return None, "Contraseña incorrecta"
        
        return None, "Usuario no encontrado"
    
    def resend_verification_code(self, email):
        """Reenvía el código de verificación"""
        users = self.sheet.get_all_records()
        for idx, user in enumerate(users, start=2):
            if user.get('Email') == email:
                # Generar nuevo código
                new_code = self.email_service.generate_verification_code()
                expiry_time = datetime.now() + timedelta(minutes=10)
                
                # Actualizar en la hoja
                self.sheet.update(f'G{idx}', new_code)  # Codigo_Verificacion
                self.sheet.update(f'H{idx}', expiry_time.isoformat())  # Codigo_Expiracion
                
                # Enviar correo
                if self.email_service.send_verification_email(email, new_code):
                    return True, "Código reenviado exitosamente"
                else:
                    return False, "Error al enviar el correo"
        
        return False, "Email no encontrado"
