# database.py - VERSIÓN DEFINITIVA CON TU ID
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
    
    def _connect(self):
        """Establece conexión con Google Sheets usando ID directo"""
        try:
            # Solo el scope de sheets, sin drive
            scope = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Intentar obtener credenciales de st.secrets (Streamlit Cloud)
            if 'google' in st.secrets:
                creds_dict = {
                    'type': st.secrets['google']['type'],
                    'project_id': st.secrets['google']['project_id'],
                    'private_key_id': st.secrets['google']['private_key_id'],
                    'private_key': st.secrets['google']['private_key'],
                    'client_email': st.secrets['google']['client_email'],
                    'client_id': st.secrets['google']['client_id'],
                    'auth_uri': st.secrets['google']['auth_uri'],
                    'token_uri': st.secrets['google']['token_uri'],
                    'auth_provider_x509_cert_url': st.secrets['google']['auth_provider_x509_cert_url'],
                    'client_x509_cert_url': st.secrets['google']['client_x509_cert_url']
                }
                
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                self.client = gspread.authorize(creds)
                
                # USAR EL ID DE TU HOJA DIRECTAMENTE
                SHEET_ID = "1ydHMo4qjmpvA-T9hvmtbRzmwBBwIgF5xvyC2jWfWkTU"
                
                try:
                    self.spreadsheet = self.client.open_by_key(SHEET_ID)
                    st.success("✅ Conectado a Google Sheets exitosamente!")
                    
                    # Verificar que existe la hoja 'Usuarios'
                    try:
                        self.spreadsheet.worksheet('Usuarios')
                        st.info("📊 Hoja 'Usuarios' encontrada")
                    except:
                        st.warning("⚠️ No se encontró la hoja 'Usuarios'. Creándola...")
                        self._create_worksheet('Usuarios', [
                            'Email', 'Nombre', 'Contraseña', 'Rol', 'Verificado',
                            'Fecha_Registro', 'Codigo_Verificacion', 'Codigo_Expiracion',
                            'Activo', 'Intentos_Fallidos', 'Bloqueado_Hasta', 'Ultimo_Login'
                        ])
                        
                except Exception as e:
                    st.error(f"❌ Error: No se pudo abrir la hoja con ID: {SHEET_ID}")
                    st.error(f"Detalle: {e}")
                    self.spreadsheet = None
                    
            else:
                st.error("❌ No hay credenciales configuradas en st.secrets")
                self.client = None
                
        except Exception as e:
            st.error(f"❌ Error de conexión a Google Sheets: {e}")
            self.client = None
    
    def _create_worksheet(self, name, headers):
        """Crea una nueva hoja de trabajo"""
        if not self.spreadsheet:
            return
        
        try:
            worksheet = self.spreadsheet.add_worksheet(name, rows=1, cols=len(headers))
            worksheet.append_row(headers)
            st.success(f"✅ Hoja '{name}' creada")
        except Exception as e:
            st.error(f"❌ Error al crear hoja '{name}': {e}")
    
    def get_worksheet(self, name):
        """Obtiene una hoja de trabajo por nombre"""
        if not self.spreadsheet:
            st.error("❌ No hay conexión a la hoja de cálculo")
            return None
        
        try:
            return self.spreadsheet.worksheet(name)
        except Exception as e:
            st.error(f"❌ Error al obtener la hoja '{name}': {e}")
            return None
    
    def get_users(self):
        """Obtiene todos los usuarios"""
        worksheet = self.get_worksheet('Usuarios')
        if not worksheet:
            return pd.DataFrame()
        
        try:
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
        worksheet = self.get_worksheet('Usuarios')
        if not worksheet:
            return False, "Error de conexión a la hoja"
        
        try:
            # Verificar si el email ya existe
            existing = self.get_user_by_email(user_data.get('Email', ''))
            if existing:
                return False, "El email ya está registrado"
            
            new_user = [
                user_data.get('Email', ''),
                user_data.get('Nombre', ''),
                user_data.get('Contraseña', ''),
                user_data.get('Rol', 'user'),
                str(user_data.get('Verificado', False)),
                datetime.now().isoformat(),
                user_data.get('Codigo_Verificacion', ''),
                user_data.get('Codigo_Expiracion', ''),
                str(user_data.get('Activo', True)),
                '0',
                '',
                ''
            ]
            
            worksheet.append_row(new_user)
            return True, "Usuario agregado exitosamente"
            
        except Exception as e:
            return False, f"Error al agregar usuario: {e}"
    
    def update_user(self, email, user_data):
        """Actualiza un usuario existente"""
        worksheet = self.get_worksheet('Usuarios')
        if not worksheet:
            return False, "Error de conexión a la hoja"
        
        try:
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
                'Nombre': 1,
                'Rol': 3,
                'Verificado': 4,
                'Activo': 8,
                'Intentos_Fallidos': 9,
                'Bloqueado_Hasta': 10,
                'Ultimo_Login': 11
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
        worksheet = self.get_worksheet('Usuarios')
        if not worksheet:
            return False
        
        try:
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
