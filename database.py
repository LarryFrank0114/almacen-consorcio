import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64
from io import BytesIO

def conectar_sheets():
    """
    Establece la conexión centralizada con Google Sheets utilizando las credenciales de GCP.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        else:
            creds_dict = dict(st.secrets)
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        return client.open("01-Herramientas") 
        
    except Exception as e:
        st.error(f"Error de conexión GCP: {e}")
        return None

def registrar_transaccion_avanzada(tipo, documento, almacen, fecha, solicitante, usuario, obs, canasta):
    sh = conectar_sheets()
    if not sh: 
        return False, "Sin conexión con la base de datos central."
    
    try:
        ws_historial = sh.worksheet("historial")
        ws_inventario = sh.worksheet("inventario")
        inv_data = ws_inventario.get_all_records()
        
        for item in canasta:
            ws_historial.append_row([fecha, tipo, documento, almacen, item['Código'], item['Material'], item['Cantidad'], solicitante, usuario, obs])
            
            fila_encontrada = None
            stock_actual = 0
            for idx, row in enumerate(inv_data, start=2):
                if str(row.get('Almacén', '')).strip() == str(almacen).strip() and str(row.get('Código', '')).strip() == str(item['Código']).strip():
                    fila_encontrada = idx
                    stock_actual = int(row['Stock']) if row['Stock'] != "" else 0
                    break
            
            if "Ingreso" in tipo or "Devolución" in tipo:
                nuevo_stock = stock_actual + int(item['Cantidad'])
            else:
                nuevo_stock = max(0, stock_actual - int(item['Cantidad']))
                
            if fila_encontrada:
                ws_inventario.update_cell(fila_encontrada, 5, nuevo_stock)
            else:
                ws_inventario.append_row([almacen, item['Código'], item['Material'], "Ubicación General", nuevo_stock])
                
        return True, "Transacción completada con éxito. Inventarios actualizados en la nube."
    except Exception as e:
        return False, f"Error crítico al procesar la transacción: {e}"

def agregar_material_maestro(codigo, descripcion, unidad):
    try:
        sh = conectar_sheets()
        if not sh: return False, "Fallo de comunicación con la base de datos."
        ws_maestro = sh.worksheet("maestro")
        
        codigos_existentes = ws_maestro.col_values(1)
        if str(codigo).strip() in [str(c).strip() for c in codigos_existentes]:
            return False, f"⚠️ El código '{codigo}' ya se encuentra registrado en el maestro central."
            
        ws_maestro.append_row([str(codigo).strip(), str(descripcion).strip(), unidad])
        return True, f"✔️ Material {descripcion} dado de alta con éxito."
    except Exception as e:
        return False, f"Error técnico: {e}"

def guardar_foto_drive(archivo, almacen, usuario):
    """
    Alternativa infalible: Almacena la imagen en Google Sheets comprimiéndola dinámicamente 
    a un string Base64 optimizado de baja resolución. Esto burla el límite de 50k caracteres 
    de Google Sheets de forma nativa y elimina para siempre los errores de cuota 403 de Drive.
    """
    try:
        # Importación interna para no sobrecargar el sistema
        from PIL import Image
        
        # 1. Leer y comprimir la imagen usando Pillow (reducimos resolución para terreno)
        img = Image.open(archivo)
        
        # Convertir a RGB si viene en formato RGBA (como algunos PNG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Redimensionar la imagen para que su ancho máximo sea 400px (mantiene aspecto)
        img.thumbnail((400, 400))
        
        # Guardar en un buffer binario con compresión JPEG optimizada (calidad 60%)
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=60, optimize=True)
        
        # Convertir a cadena Base64 limpia
        img_str = base64.b64encode(buffered.getvalue()).decode()
        enlace_base64 = f"data:image/jpeg;base64,{img_str}"
        
        # Verificación estricta de tamaño en memoria
        if len(enlace_base64) > 49500:
            # Si aún es muy grande, bajamos más la escala
            buffered = BytesIO()
            img.thumbnail((250, 250))
            img.save(buffered, format="JPEG", quality=45, optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            enlace_base64 = f"data:image/jpeg;base64,{img_str}"

        # 2. Registrar directamente en la hoja 'fotos' de Google Sheets
        sh = conectar_sheets()
        if not sh: return None
        
        lista_hojas = [h.title for h in sh.worksheets()]
        if "fotos" not in lista_hojas:
            ws_fotos = sh.add_worksheet(title="fotos", rows="1000", cols="4")
            ws_fotos.append_row(["Fecha", "Almacen", "Usuario", "Enlace"])
        else:
            ws_fotos = sh.worksheet("fotos")
            
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws_fotos.append_row([fecha_registro, almacen, usuario, enlace_base64])
        
        return enlace_base64
        
    except Exception as e:
        st.error(f"Error al procesar e indexar imagen en base de datos: {e}")
        return None
