# services.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import re

class InventoryService:
    """Servicio para gestionar el inventario del almacén"""
    
    def __init__(self):
        self.sheet = self._connect_to_sheets()
        self._initialize_sheets()
    
    def _connect_to_sheets(self):
        """Conecta a Google Sheets para el inventario"""
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
            
            # Abrir o crear la hoja de inventario
            try:
                spreadsheet = client.open('Almacen_Inventario')
            except:
                spreadsheet = client.create('Almacen_Inventario')
                # Compartir con el correo de la cuenta de servicio
                spreadsheet.share(os.getenv('EMAIL_FROM'), perm_type='user', role='writer')
            
            return spreadsheet
            
        except Exception as e:
            st.error(f"❌ Error de conexión a la base de datos: {e}")
            return None
    
    def _initialize_sheets(self):
        """Inicializa las hojas necesarias si no existen"""
        if not self.sheet:
            return
        
        # Hojas necesarias
        sheets = {
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
                'Dirección', 'Notas'
            ],
            'Categorías': [
                'ID', 'Nombre', 'Descripción', 'Activo'
            ]
        }
        
        for sheet_name, headers in sheets.items():
            try:
                worksheet = self.sheet.worksheet(sheet_name)
            except:
                worksheet = self.sheet.add_worksheet(sheet_name, rows=1, cols=len(headers))
                worksheet.append_row(headers)
    
    # ==================== PRODUCTOS ====================
    
    def get_all_products(self):
        """Obtiene todos los productos"""
        if not self.sheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.sheet.worksheet('Productos')
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error al obtener productos: {e}")
            return pd.DataFrame()
    
    def get_product_by_id(self, product_id):
        """Obtiene un producto por su ID"""
        products = self.get_all_products()
        if products.empty:
            return None
        
        product = products[products['ID'] == product_id]
        if product.empty:
            return None
        
        return product.iloc[0].to_dict()
    
    def get_product_by_code(self, code):
        """Obtiene un producto por su código"""
        products = self.get_all_products()
        if products.empty:
            return None
        
        product = products[products['Código'] == code]
        if product.empty:
            return None
        
        return product.iloc[0].to_dict()
    
    def search_products(self, search_term):
        """Busca productos por nombre, código o categoría"""
        products = self.get_all_products()
        if products.empty:
            return pd.DataFrame()
        
        # Búsqueda en múltiples campos
        mask = (
            products['Nombre'].str.contains(search_term, case=False, na=False) |
            products['Código'].str.contains(search_term, case=False, na=False) |
            products['Categoría'].str.contains(search_term, case=False, na=False) |
            products['Descripción'].str.contains(search_term, case=False, na=False)
        )
        
        return products[mask]
    
    def add_product(self, product_data):
        """Agrega un nuevo producto"""
        if not self.sheet:
            return False, "Error de conexión a la base de datos"
        
        try:
            worksheet = self.sheet.worksheet('Productos')
            
            # Generar ID único
            products = self.get_all_products()
            new_id = len(products) + 1 if not products.empty else 1
            
            # Procesar imagen si existe
            imagen_data = product_data.get('Imagen', '')
            if imagen_data and isinstance(imagen_data, bytes):
                # Comprimir y codificar imagen
                imagen_data = self._compress_image(imagen_data)
            
            # Preparar datos del producto
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
                True  # Activo
            ]
            
            worksheet.append_row(new_product)
            
            # Registrar movimiento
            self._log_movement(new_id, 'entrada', product_data.get('Cantidad', 0), 
                             'Creación de producto', f"Producto agregado: {product_data.get('Nombre', '')}")
            
            return True, "✅ Producto agregado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al agregar producto: {e}"
    
    def update_product(self, product_id, product_data):
        """Actualiza un producto existente"""
        if not self.sheet:
            return False, "Error de conexión a la base de datos"
        
        try:
            worksheet = self.sheet.worksheet('Productos')
            products = self.get_all_products()
            
            if products.empty:
                return False, "No hay productos registrados"
            
            # Encontrar el producto
            idx = products[products['ID'] == product_id].index
            if len(idx) == 0:
                return False, "Producto no encontrado"
            
            row_num = idx[0] + 2  # +2 porque el índice 0 es fila 1 (encabezado)
            
            # Obtener datos actuales
            current_row = worksheet.row_values(row_num)
            
            # Actualizar solo los campos proporcionados
            current_data = {
                'ID': product_id,
                'Código': product_data.get('Código', current_row[1]),
                'Nombre': product_data.get('Nombre', current_row[2]),
                'Categoría': product_data.get('Categoría', current_row[3]),
                'Descripción': product_data.get('Descripción', current_row[4]),
                'Cantidad': product_data.get('Cantidad', current_row[5]),
                'Precio_Compra': product_data.get('Precio_Compra', current_row[6]),
                'Precio_Venta': product_data.get('Precio_Venta', current_row[7]),
                'Proveedor': product_data.get('Proveedor', current_row[8]),
                'Ubicación': product_data.get('Ubicación', current_row[9]),
                'Stock_Mínimo': product_data.get('Stock_Mínimo', current_row[10]),
                'Stock_Máximo': product_data.get('Stock_Máximo', current_row[11]),
                'Fecha_Ingreso': current_row[12],
                'Última_Actualización': datetime.now().isoformat(),
                'Imagen': product_data.get('Imagen', current_row[14]),
                'Activo': product_data.get('Activo', current_row[15])
            }
            
            # Actualizar fila
            update_row = [
                current_data['ID'],
                current_data['Código'],
                current_data['Nombre'],
                current_data['Categoría'],
                current_data['Descripción'],
                current_data['Cantidad'],
                current_data['Precio_Compra'],
                current_data['Precio_Venta'],
                current_data['Proveedor'],
                current_data['Ubicación'],
                current_data['Stock_Mínimo'],
                current_data['Stock_Máximo'],
                current_data['Fecha_Ingreso'],
                current_data['Última_Actualización'],
                current_data['Imagen'],
                current_data['Activo']
            ]
            
            worksheet.update(f'A{row_num}:P{row_num}', [update_row])
            
            # Registrar movimiento
            self._log_movement(product_id, 'actualización', 0,
                             'Actualización de producto', f"Producto actualizado: {current_data['Nombre']}")
            
            return True, "✅ Producto actualizado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al actualizar producto: {e}"
    
    def delete_product(self, product_id):
        """Elimina un producto (desactiva)"""
        if not self.sheet:
            return False, "Error de conexión a la base de datos"
        
        try:
            worksheet = self.sheet.worksheet('Productos')
            products = self.get_all_products()
            
            if products.empty:
                return False, "No hay productos registrados"
            
            idx = products[products['ID'] == product_id].index
            if len(idx) == 0:
                return False, "Producto no encontrado"
            
            row_num = idx[0] + 2
            
            # Desactivar producto
            worksheet.update(f'P{row_num}', 'False')
            
            return True, "✅ Producto eliminado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al eliminar producto: {e}"
    
    def update_stock(self, product_id, cantidad, tipo='entrada', motivo='', notas=''):
        """Actualiza el stock de un producto"""
        if not self.sheet:
            return False, "Error de conexión a la base de datos"
        
        try:
            worksheet = self.sheet.worksheet('Productos')
            products = self.get_all_products()
            
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
            
            # Actualizar cantidad
            worksheet.update(f'F{row_num}', str(new_qty))
            worksheet.update(f'N{row_num}', datetime.now().isoformat())
            
            # Registrar movimiento
            self._log_movement(product_id, tipo, cantidad, motivo, notas)
            
            # Verificar stock mínimo
            stock_min = int(products.iloc[idx[0]]['Stock_Mínimo'])
            if new_qty <= stock_min:
                return True, f"⚠️ Producto con stock bajo: {new_qty} unidades (mínimo: {stock_min})"
            
            return True, f"✅ Stock actualizado: {new_qty} unidades"
            
        except Exception as e:
            return False, f"❌ Error al actualizar stock: {e}"
    
    # ==================== MOVIMIENTOS ====================
    
    def _log_movement(self, product_id, tipo, cantidad, motivo, notas=''):
        """Registra un movimiento en el historial"""
        if not self.sheet:
            return
        
        try:
            worksheet = self.sheet.worksheet('Movimientos')
            
            # Obtener movimientos existentes
            movements = self.get_all_movements()
            new_id = len(movements) + 1 if not movements.empty else 1
            
            # Datos del usuario actual
            user = st.session_state.get('user', {})
            usuario = user.get('nombre', 'Sistema')
            
            # Registrar movimiento
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
            
        except Exception as e:
            st.error(f"❌ Error al registrar movimiento: {e}")
    
    def get_all_movements(self):
        """Obtiene todos los movimientos"""
        if not self.sheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.sheet.worksheet('Movimientos')
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error al obtener movimientos: {e}")
            return pd.DataFrame()
    
    def get_product_movements(self, product_id):
        """Obtiene los movimientos de un producto específico"""
        movements = self.get_all_movements()
        if movements.empty:
            return pd.DataFrame()
        
        return movements[movements['Producto_ID'] == product_id]
    
    # ==================== PROVEEDORES ====================
    
    def get_all_suppliers(self):
        """Obtiene todos los proveedores"""
        if not self.sheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.sheet.worksheet('Proveedores')
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error al obtener proveedores: {e}")
            return pd.DataFrame()
    
    def add_supplier(self, supplier_data):
        """Agrega un nuevo proveedor"""
        if not self.sheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.sheet.worksheet('Proveedores')
            suppliers = self.get_all_suppliers()
            new_id = len(suppliers) + 1 if not suppliers.empty else 1
            
            worksheet.append_row([
                new_id,
                supplier_data.get('Nombre', ''),
                supplier_data.get('Contacto', ''),
                supplier_data.get('Teléfono', ''),
                supplier_data.get('Email', ''),
                supplier_data.get('Dirección', ''),
                supplier_data.get('Notas', '')
            ])
            
            return True, "✅ Proveedor agregado exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al agregar proveedor: {e}"
    
    # ==================== CATEGORÍAS ====================
    
    def get_all_categories(self):
        """Obtiene todas las categorías"""
        if not self.sheet:
            return pd.DataFrame()
        
        try:
            worksheet = self.sheet.worksheet('Categorías')
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error al obtener categorías: {e}")
            return pd.DataFrame()
    
    def add_category(self, category_data):
        """Agrega una nueva categoría"""
        if not self.sheet:
            return False, "Error de conexión"
        
        try:
            worksheet = self.sheet.worksheet('Categorías')
            categories = self.get_all_categories()
            new_id = len(categories) + 1 if not categories.empty else 1
            
            worksheet.append_row([
                new_id,
                category_data.get('Nombre', ''),
                category_data.get('Descripción', ''),
                True
            ])
            
            return True, "✅ Categoría agregada exitosamente"
            
        except Exception as e:
            return False, f"❌ Error al agregar categoría: {e}"
    
    # ==================== REPORTES ====================
    
    def get_stock_report(self):
        """Genera un reporte de stock"""
        products = self.get_all_products()
        if products.empty:
            return pd.DataFrame()
        
        # Calcular métricas
        report = products.copy()
        report['Valor_Inventario'] = report['Cantidad'] * report['Precio_Compra']
        report['Estado_Stock'] = report.apply(
            lambda row: 'Crítico' if row['Cantidad'] <= row['Stock_Mínimo'] 
            else 'Alto' if row['Cantidad'] >= row['Stock_Máximo']
            else 'Normal',
            axis=1
        )
        
        return report
    
    def get_dashboard_metrics(self):
        """Obtiene métricas para el dashboard"""
        products = self.get_all_products()
        if products.empty:
            return {
                'total_products': 0,
                'total_value': 0,
                'low_stock': 0,
                'categories': 0,
                'total_movements': 0
            }
        
        # Calcular métricas
        total_products = len(products)
        total_value = (products['Cantidad'] * products['Precio_Compra']).sum()
        low_stock = len(products[products['Cantidad'] <= products['Stock_Mínimo']])
        
        categories = self.get_all_categories()
        total_categories = len(categories)
        
        movements = self.get_all_movements()
        total_movements = len(movements)
        
        return {
            'total_products': total_products,
            'total_value': total_value,
            'low_stock': low_stock,
            'categories': total_categories,
            'total_movements': total_movements
        }
    
    # ==================== UTILIDADES ====================
    
    def _compress_image(self, image_data, max_size=(800, 800), quality=85):
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
    
    def get_products_by_category(self, category):
        """Obtiene productos por categoría"""
        products = self.get_all_products()
        if products.empty:
            return pd.DataFrame()
        
        return products[products['Categoría'] == category]
    
    def get_low_stock_products(self):
        """Obtiene productos con stock bajo"""
        products = self.get_all_products()
        if products.empty:
            return pd.DataFrame()
        
        return products[products['Cantidad'] <= products['Stock_Mínimo']]
    
    def export_to_excel(self):
        """Exporta todos los datos a un archivo Excel"""
        try:
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Escribir todas las hojas
                for sheet_name in ['Productos', 'Movimientos', 'Proveedores', 'Categorías']:
                    try:
                        df = self.sheet.worksheet(sheet_name).get_all_records()
                        pd.DataFrame(df).to_excel(writer, sheet_name=sheet_name, index=False)
                    except:
                        pass
            
            output.seek(0)
            return output
            
        except Exception as e:
            st.error(f"❌ Error al exportar: {e}")
            return None
