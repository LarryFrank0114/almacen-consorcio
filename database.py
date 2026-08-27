# database.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
import os

class Database:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self._connect()
        self._initialize_spreadsheet()
    
    def _connect(self):
        """Establece conexión con Google Sheets"""
        try:
            # Intentar obtener credenciales de st.secrets (Streamlit Cloud)
            if 'google' in st.secrets:
                credentials = st.secrets['google']
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(credentials, scopes=scope)
                self.client = gspread.authorize(creds)
            else:
                # Para desarrollo local
                from dotenv import load_dotenv
                load_dotenv()
                creds_dict = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS'))
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                self.client = gspread.authorize(creds)
                
        except Exception as e:
            st.error(f"❌ Error de conexión a Google Sheets: {e}")
            self.client = None
    
    def _initialize_spreadsheet(self):
        """Inicializa el spreadsheet principal"""
        if not self.client:
            return
        
        try:
            # Intentar abrir el spreadsheet existente
            try:
                self.spreadsheet = self.client.open('Almacen_Consorcio')
            except:
                # Crear nuevo spreadsheet
                self.spreadsheet = self.client.create('Almacen_Consorcio')
                
                # Obtener email para compartir
                try:
                    share_email = st.secrets.get('secrets', {}).get('email_from', '')
                except:
                    share_email = os.getenv('EMAIL_FROM', '')
                
                if share_email:
                    self.spreadsheet.share(share_email, perm_type='user', role='writer')
            
            # Crear las hojas necesarias
            self._create_worksheets()
            
        except Exception as e:
            st.error(f"❌ Error al inicializar spreadsheet: {e}")
            self.spreadsheet = None
    
    def _create_worksheets(self):
        """Crea las hojas de trabajo necesarias si no existen"""
        if not self.spreadsheet:
            return
        
        worksheets_config = {
            'Usuarios': [
                'Email', 'Nombre', 'Contraseña', 'Rol', 'Verificado',
                'Fecha_Registro', 'Codigo_Verificacion', 'Codigo_Expiracion',
                'Activo', 'Intentos_Fallidos', 'Bloqueado_Hasta', 'Ultimo_Login'
            ],
            'Productos': [
                'ID', 'Código', 'Nombre', 'Categoría', 'Descripción',
                'Cantidad', 'Precio_Compra', 'Precio_Venta', 'Proveedor',
                'Ubicación', 'Stock_Mínimo', 'Stock_Máximo', 'Fecha_Ingreso',
                'Última_Actualización', 'Imagen', 'Activo'
            ],
            'Movimientos': [
                'ID', 'Producto_ID', 'Tipo', 'Cantidad', 'Fecha',
                'Usuario', 'Motivo', 'Notas'
            ],
            'Proveedores': [
                'ID', 'Nombre', 'Contacto', 'Teléfono', 'Email',
                'Dirección', 'Notas', 'Activo'
            ],
            'Categorías': [
                'ID', 'Nombre', 'Descripción', 'Activo'
            ],
            'Auditoría': [
                'ID', 'Usuario', 'Acción', 'Tabla', 'Registro_ID',
                'Fecha', 'Detalles', 'IP'
            ]
        }
        
        for sheet_name, headers in worksheets_config.items():
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except:
                worksheet = self.spreadsheet.add_worksheet(sheet_name, rows=1, cols=len(headers))
                worksheet.append_row(headers)
    
    # Resto de métodos igual que antes...
    def get_users(self):
        """Obtiene todos los usuarios"""
        if not self.spreadsheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.spreadsheet.worksheet('Usuarios')
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error al obtener usuarios: {e}")
            return pd.DataFrame()
    
    def get_user_by_email(self, email):
        """Obtiene un usuario por su email"""
        users = self.get_users()
        if users.empty:
            return None
        
        user = users[users['Email'] == email]
        if user.empty:
            return None
        
        return user.iloc[0].to_dict()
    
    def add_user(self, user_data):
        """Agrega un nuevo usuario"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Usuarios')
            
            # Verificar si el email ya existe
            existing = self.get_user_by_email(user_data.get('Email', ''))
            if existing:
                return False, "El email ya está registrado"
            
            new_user = [
                user_data.get('Email', ''),
                user_data.get('Nombre', ''),
                user_data.get('Contraseña', ''),
                user_data.get('Rol', 'user'),
                user_data.get('Verificado', False),
                datetime.now().isoformat(),
                user_data.get('Codigo_Verificacion', ''),
                user_data.get('Codigo_Expiracion', ''),
                user_data.get('Activo', True),
                0,
                '',
                ''
            ]
            
            worksheet.append_row(new_user)
            return True, "Usuario agregado exitosamente"
            
        except Exception as e:
            return False, f"Error al agregar usuario: {e}"
    
    def update_user(self, email, user_data):
        """Actualiza un usuario existente"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Usuarios')
            users = self.get_users()
            
            if users.empty:
                return False, "No hay usuarios registrados"
            
            idx = users[users['Email'] == email].index
            if len(idx) == 0:
                return False, "Usuario no encontrado"
            
            row_num = idx[0] + 2
            current_row = worksheet.row_values(row_num)
            update_row = current_row.copy()
            
            campos = {
                'Nombre': 1, 'Rol': 3, 'Verificado': 4,
                'Activo': 8, 'Intentos_Fallidos': 9,
                'Bloqueado_Hasta': 10, 'Ultimo_Login': 11
            }
            
            for field, index in campos.items():
                if field in user_data:
                    update_row[index] = str(user_data[field])
            
            worksheet.update(f'A{row_num}:L{row_num}', [update_row])
            return True, "Usuario actualizado exitosamente"
            
        except Exception as e:
            return False, f"Error al actualizar usuario: {e}"
    
    def update_user_verification(self, email, code, expiry):
        """Actualiza el código de verificación de un usuario"""
        if not self.spreadsheet:
            return False
        
        try:
            worksheet = self.spreadsheet.worksheet('Usuarios')
            users = self.get_users()
            
            if users.empty:
                return False
            
            idx = users[users['Email'] == email].index
            if len(idx) == 0:
                return False
            
            row_num = idx[0] + 2
            worksheet.update(f'G{row_num}', code)
            worksheet.update(f'H{row_num}', expiry)
            return True
            
        except Exception as e:
            st.error(f"❌ Error al actualizar verificación: {e}")
            return False
    
    def mark_user_as_verified(self, email):
        """Marca un usuario como verificado"""
        return self.update_user(email, {'Verificado': True})
