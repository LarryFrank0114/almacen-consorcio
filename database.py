# database.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
import re

class Database:
    """Clase principal para manejar todas las operaciones de base de datos"""
    
    def __init__(self):
        self.client = None
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
                creds_dict = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS'))
                scope = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                self.client = gspread.authorize(creds)
                
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
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
                # Compartir con el correo configurado
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
        
        # Definición de hojas y sus encabezados
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
    
    # ==================== OPERACIONES DE USUARIOS ====================
    
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
            
            # Preparar datos
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
                0,  # Intentos_Fallidos
                '',  # Bloqueado_Hasta
                ''   # Ultimo_Login
            ]
            
            worksheet.append_row(new_user)
            
            # Registrar en auditoría
            self.audit_log('Creación', 'Usuarios', user_data.get('Email', ''), 
                          f"Usuario creado: {user_data.get('Nombre', '')}")
            
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
            
            # Encontrar el usuario
            idx = users[users['Email'] == email].index
            if len(idx) == 0:
                return False, "Usuario no encontrado"
            
            row_num = idx[0] + 2  # +2 por el encabezado
            
            # Obtener datos actuales
            current_row = worksheet.row_values(row_num)
            
            # Actualizar solo los campos proporcionados
            update_row = current_row.copy()
            
            if 'Nombre' in user_data:
                update_row[1] = user_data['Nombre']
            if 'Rol' in user_data:
                update_row[3] = user_data['Rol']
            if 'Verificado' in user_data:
                update_row[4] = str(user_data['Verificado'])
            if 'Activo' in user_data:
                update_row[8] = str(user_data['Activo'])
            if 'Intentos_Fallidos' in user_data:
                update_row[9] = str(user_data['Intentos_Fallidos'])
            if 'Bloqueado_Hasta' in user_data:
                update_row[10] = user_data['Bloqueado_Hasta']
            if 'Ultimo_Login' in user_data:
                update_row[11] = user_data['Ultimo_Login']
            
            worksheet.update(f'A{row_num}:L{row_num}', [update_row])
            
            # Registrar en auditoría
            self.audit_log('Actualización', 'Usuarios', email, 
                          f"Usuario actualizado: {user_data.get('Nombre', '')}")
            
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
            
            # Actualizar código y expiración (columnas G y H)
            worksheet.update(f'G{row_num}', code)
            worksheet.update(f'H{row_num}', expiry)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al actualizar verificación: {e}")
            return False
    
    def mark_user_as_verified(self, email):
        """Marca un usuario como verificado"""
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
            
            # Marcar como verificado (columna E)
            worksheet.update(f'E{row_num}', 'True')
            
            # Registrar en auditoría
            self.audit_log('Verificación', 'Usuarios', email, 'Usuario verificado por correo')
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al marcar como verificado: {e}")
            return False
    
    # ==================== OPERACIONES DE PRODUCTOS ====================
    
    def get_products(self, active_only=True):
        """Obtiene todos los productos"""
        if not self.spreadsheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.spreadsheet.worksheet('Productos')
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if active_only and not df.empty:
                df = df[df['Activo'] == True]
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al obtener productos: {e}")
            return pd.DataFrame()
    
    def get_product_by_id(self, product_id):
        """Obtiene un producto por su ID"""
        products = self.get_products(active_only=False)
        if products.empty:
            return None
        
        product = products[products['ID'] == product_id]
        if product.empty:
            return None
        
        return product.iloc[0].to_dict()
    
    def add_product(self, product_data):
        """Agrega un nuevo producto"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Productos')
            products = self.get_products(active_only=False)
            
            # Generar nuevo ID
            new_id = len(products) + 1 if not products.empty else 1
            
            # Procesar imagen si existe
            imagen_data = product_data.get('Imagen', '')
            if imagen_data and isinstance(imagen_data, bytes):
                imagen_data = self.compress_image(imagen_data)
            
            # Preparar datos
            new_product = [
                new_id,
                product_data.get('Código', f'PROD-{new_id:04d}'),
                product_data.get('Nombre', ''),
                product_data.get('Categoría', 'General'),
                product_data.get('Descripción', ''),
                int(product_data.get('Cantidad', 0)),
                float(product_data.get('Precio_Compra', 0)),
                float(product_data.get('Precio_Venta', 0)),
                product_data.get('Proveedor', ''),
                product_data.get('Ubicación', ''),
                int(product_data.get('Stock_Mínimo', 0)),
                int(product_data.get('Stock_Máximo', 0)),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                imagen_data,
                True
            ]
            
            worksheet.append_row(new_product)
            
            # Registrar movimiento inicial
            self.add_movement(
                product_id=new_id,
                tipo='entrada',
                cantidad=product_data.get('Cantidad', 0),
                motivo='Creación de producto',
                notas=f"Producto agregado: {product_data.get('Nombre', '')}"
            )
            
            # Registrar en auditoría
            self.audit_log('Creación', 'Productos', new_id, 
                          f"Producto creado: {product_data.get('Nombre', '')}")
            
            return True, "✅ Producto agregado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al agregar producto: {e}"
    
    def update_product(self, product_id, product_data):
        """Actualiza un producto existente"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Productos')
            products = self.get_products(active_only=False)
            
            if products.empty:
                return False, "No hay productos registrados"
            
            idx = products[products['ID'] == product_id].index
            if len(idx) == 0:
                return False, "Producto no encontrado"
            
            row_num = idx[0] + 2
            
            # Obtener datos actuales
            current_row = worksheet.row_values(row_num)
            
            # Actualizar solo los campos proporcionados
            update_row = current_row.copy()
            
            campos = {
                'Código': 1, 'Nombre': 2, 'Categoría': 3, 'Descripción': 4,
                'Cantidad': 5, 'Precio_Compra': 6, 'Precio_Venta': 7,
                'Proveedor': 8, 'Ubicación': 9, 'Stock_Mínimo': 10,
                'Stock_Máximo': 11, 'Imagen': 14, 'Activo': 15
            }
            
            for field, index in campos.items():
                if field in product_data:
                    update_row[index] = product_data[field]
            
            # Actualizar fecha
            update_row[13] = datetime.now().isoformat()
            
            worksheet.update(f'A{row_num}:P{row_num}', [update_row])
            
            # Registrar en auditoría
            self.audit_log('Actualización', 'Productos', product_id, 
                          f"Producto actualizado: {product_data.get('Nombre', '')}")
            
            return True, "✅ Producto actualizado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al actualizar producto: {e}"
    
    def update_stock(self, product_id, cantidad, tipo='entrada', motivo='', notas=''):
        """Actualiza el stock de un producto"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Productos')
            products = self.get_products(active_only=False)
            
            if products.empty:
                return False, "No hay productos registrados"
            
            idx = products[products['ID'] == product_id].index
            if len(idx) == 0:
                return False, "Producto no encontrado"
            
            row_num = idx[0] + 2
            
            # Obtener cantidad actual
            current_qty = int(products.iloc[idx[0]]['Cantidad'])
            
            # Calcular nueva cantidad
            if tipo == 'entrada':
                new_qty = current_qty + cantidad
            elif tipo == 'salida':
                if current_qty < cantidad:
                    return False, f"❌ Stock insuficiente. Disponible: {current_qty}"
                new_qty = current_qty - cantidad
            else:
                return False, "❌ Tipo de movimiento inválido"
            
            # Actualizar cantidad y fecha
            worksheet.update(f'F{row_num}', str(new_qty))
            worksheet.update(f'N{row_num}', datetime.now().isoformat())
            
            # Registrar movimiento
            user = st.session_state.get('user', {})
            usuario = user.get('nombre', 'Sistema')
            
            self.add_movement(
                product_id=product_id,
                tipo=tipo,
                cantidad=cantidad,
                motivo=motivo,
                notas=notas,
                usuario=usuario
            )
            
            # Verificar stock mínimo
            stock_min = int(products.iloc[idx[0]]['Stock_Mínimo'])
            if new_qty <= stock_min:
                return True, f"⚠️ Producto con stock bajo: {new_qty} unidades (mínimo: {stock_min})"
            
            return True, f"✅ Stock actualizado: {new_qty} unidades"
            
        except Exception as e:
            return False, f"❌ Error al actualizar stock: {e}"
    
    # ==================== OPERACIONES DE MOVIMIENTOS ====================
    
    def get_movements(self, limit=None):
        """Obtiene todos los movimientos"""
        if not self.spreadsheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.spreadsheet.worksheet('Movimientos')
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if limit and not df.empty:
                df = df.tail(limit)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al obtener movimientos: {e}")
            return pd.DataFrame()
    
    def add_movement(self, product_id, tipo, cantidad, motivo, notas='', usuario='Sistema'):
        """Agrega un nuevo movimiento"""
        if not self.spreadsheet:
            return False
        
        try:
            worksheet = self.spreadsheet.worksheet('Movimientos')
            movements = self.get_movements()
            
            new_id = len(movements) + 1 if not movements.empty else 1
            
            worksheet.append_row([
                new_id,
                product_id,
                tipo,
                cantidad,
                datetime.now().isoformat(),
                usuario,
                motivo,
                notas
            ])
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al agregar movimiento: {e}")
            return False
    
    def get_product_movements(self, product_id):
        """Obtiene los movimientos de un producto específico"""
        movements = self.get_movements()
        if movements.empty:
            return pd.DataFrame()
        
        return movements[movements['Producto_ID'] == product_id]
    
    # ==================== OPERACIONES DE PROVEEDORES ====================
    
    def get_suppliers(self, active_only=True):
        """Obtiene todos los proveedores"""
        if not self.spreadsheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.spreadsheet.worksheet('Proveedores')
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if active_only and not df.empty and 'Activo' in df.columns:
                df = df[df['Activo'] == True]
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al obtener proveedores: {e}")
            return pd.DataFrame()
    
    def add_supplier(self, supplier_data):
        """Agrega un nuevo proveedor"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Proveedores')
            suppliers = self.get_suppliers(active_only=False)
            
            new_id = len(suppliers) + 1 if not suppliers.empty else 1
            
            worksheet.append_row([
                new_id,
                supplier_data.get('Nombre', ''),
                supplier_data.get('Contacto', ''),
                supplier_data.get('Teléfono', ''),
                supplier_data.get('Email', ''),
                supplier_data.get('Dirección', ''),
                supplier_data.get('Notas', ''),
                True
            ])
            
            # Registrar en auditoría
            self.audit_log('Creación', 'Proveedores', new_id, 
                          f"Proveedor creado: {supplier_data.get('Nombre', '')}")
            
            return True, "✅ Proveedor agregado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al agregar proveedor: {e}"
    
    # ==================== OPERACIONES DE CATEGORÍAS ====================
    
    def get_categories(self, active_only=True):
        """Obtiene todas las categorías"""
        if not self.spreadsheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.spreadsheet.worksheet('Categorías')
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if active_only and not df.empty and 'Activo' in df.columns:
                df = df[df['Activo'] == True]
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al obtener categorías: {e}")
            return pd.DataFrame()
    
    def add_category(self, category_data):
        """Agrega una nueva categoría"""
        if not self.spreadsheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.spreadsheet.worksheet('Categorías')
            categories = self.get_categories(active_only=False)
            
            new_id = len(categories) + 1 if not categories.empty else 1
            
            worksheet.append_row([
                new_id,
                category_data.get('Nombre', ''),
                category_data.get('Descripción', ''),
                True
            ])
            
            # Registrar en auditoría
            self.audit_log('Creación', 'Categorías', new_id, 
                          f"Categoría creada: {category_data.get('Nombre', '')}")
            
            return True, "✅ Categoría agregada exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al agregar categoría: {e}"
    
    # ==================== AUDITORÍA ====================
    
    def audit_log(self, accion, tabla, registro_id, detalles=''):
        """Registra una acción en el log de auditoría"""
        if not self.spreadsheet:
            return
        
        try:
            worksheet = self.spreadsheet.worksheet('Auditoría')
            audit_data = self.get_audit_log()
            
            new_id = len(audit_data) + 1 if not audit_data.empty else 1
            
            user = st.session_state.get('user', {})
            usuario = user.get('email', 'Sistema')
            
            worksheet.append_row([
                new_id,
                usuario,
                accion,
                tabla,
                registro_id,
                datetime.now().isoformat(),
                detalles,
                ''  # IP (opcional)
            ])
            
        except Exception as e:
            st.error(f"❌ Error al registrar auditoría: {e}")
    
    def get_audit_log(self, limit=100):
        """Obtiene el log de auditoría"""
        if not self.spreadsheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.spreadsheet.worksheet('Auditoría')
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if not df.empty:
                df = df.tail(limit)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error al obtener auditoría: {e}")
            return pd.DataFrame()
    
    # ==================== UTILIDADES ====================
    
    def compress_image(self, image_data, max_size=(800, 800), quality=85):
        """Comprime y redimensiona una imagen"""
        try:
            # Abrir imagen
            img = Image.open(BytesIO(image_data))
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar manteniendo aspecto
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Guardar en buffer
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            # Codificar a base64
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Error al comprimir imagen: {e}")
            return ''
    
    def decode_image(self, base64_string):
        """Decodifica una imagen desde base64"""
        if not base64_string:
            return None
        
        try:
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        except:
            return None
    
    def generate_id(self, prefix='', length=8):
        """Genera un ID único"""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        return f"{prefix}{''.join(random.choices(chars, k=length))}"
    
    # ==================== REPORTES ====================
    
    def get_stock_report(self):
        """Genera un reporte completo de stock"""
        products = self.get_products()
        if products.empty:
            return pd.DataFrame()
        
        report = products.copy()
        
        # Calcular valor del inventario
        report['Valor_Inventario'] = report['Cantidad'] * report['Precio_Compra']
        report['Ganancia_Potencial'] = report['Cantidad'] * (report['Precio_Venta'] - report['Precio_Compra'])
        
        # Estado del stock
        report['Estado_Stock'] = report.apply(
            lambda row: 'Crítico' if row['Cantidad'] <= row['Stock_Mínimo']
            else 'Excedente' if row['Cantidad'] >= row['Stock_Máximo']
            else 'Normal',
            axis=1
        )
        
        # Rotación (basado en movimientos)
        movements = self.get_movements()
        if not movements.empty:
            mov_count = movements.groupby('Producto_ID').size().to_dict()
            report['Movimientos'] = report['ID'].map(mov_count).fillna(0)
        else:
            report['Movimientos'] = 0
        
        return report
    
    def get_dashboard_metrics(self):
        """Obtiene métricas para el dashboard"""
        products = self.get_products()
        if products.empty:
            return {
                'total_products': 0,
                'total_value': 0,
                'low_stock': 0,
                'categories': 0,
                'total_movements': 0,
                'total_suppliers': 0
            }
        
        # Calcular métricas
        total_products = len(products)
        total_value = (products['Cantidad'] * products['Precio_Compra']).sum()
        low_stock = len(products[products['Cantidad'] <= products['Stock_Mínimo']])
        
        categories = self.get_categories()
        total_categories = len(categories)
        
        movements = self.get_movements()
        total_movements = len(movements)
        
        suppliers = self.get_suppliers()
        total_suppliers = len(suppliers)
        
        # Productos más recientes
        recent_products = products.nlargest(5, 'Fecha_Ingreso') if not products.empty else pd.DataFrame()
        
        return {
            'total_products': total_products,
            'total_value': total_value,
            'low_stock': low_stock,
            'categories': total_categories,
            'total_movements': total_movements,
            'total_suppliers': total_suppliers,
            'recent_products': recent_products[['Nombre', 'Cantidad', 'Fecha_Ingreso']].to_dict('records') if not recent_products.empty else []
        }
    
    # ==================== MANTENIMIENTO ====================
    
    def cleanup_old_data(self, days=30):
        """Limpia datos antiguos (movimientos y auditoría)"""
        try:
            # Limpiar movimientos antiguos
            movements = self.get_movements()
            if not movements.empty:
                movements['Fecha'] = pd.to_datetime(movements['Fecha'])
                old_movements = movements[movements['Fecha'] < datetime.now() - pd.Timedelta(days=days)]
                
                if not old_movements.empty:
                    # Aquí podrías archivar o eliminar
                    st.info(f"📦 {len(old_movements)} movimientos antiguos encontrados")
            
            # Limpiar auditoría antigua
            audit = self.get_audit_log()
            if not audit.empty:
                audit['Fecha'] = pd.to_datetime(audit['Fecha'])
                old_audit = audit[audit['Fecha'] < datetime.now() - pd.Timedelta(days=days)]
                
                if not old_audit.empty:
                    st.info(f"📋 {len(old_audit)} registros de auditoría antiguos encontrados")
            
            return True, "Limpieza completada"
            
        except Exception as e:
            return False, f"Error en limpieza: {e}"
