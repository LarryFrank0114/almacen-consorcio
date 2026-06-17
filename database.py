import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

def conectar_sheets():
    """
    Establece la conexión segura con Google Sheets y Google Drive.
    Extrae el valor crudo del string JSON para evitar que Streamlit devuelva
    un objeto Response [200].
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "google_sheets_json" in st.secrets:
            # 💡 Forzamos a obtener el valor en texto puro si Streamlit lo encapsuló
            json_texto = st.secrets["google_sheets_json"]
            if hasattr(json_texto, "value"):
                json_texto = json_texto.value
                
            # Limpiamos espacios en blanco o saltos de línea fantasmas
            json_texto = json_texto.strip()
            
            # Convertimos el texto a un diccionario real de Python
            creds_dict = json.loads(json_texto)
        else:
            creds_dict = dict(st.secrets)
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abre el libro principal de control logístico del consorcio
        return client.open("01 - Herramientas") 
    except Exception as e:
        st.error(f"Error de conexión GCP: {e}")
        return None

def registrar_transaccion_avanzada(tipo, documento, almacen, fecha, solicitante, usuario, obs, canasta):
    """
    Procesa la canasta de materiales afectando dinámicamente las existencias
    en la pestaña 'inventario' y dejando rastro en la pestaña 'historial'.
    """
    sh = conectar_sheets()
    if not sh: 
        return False, "Sin conexión con la base de datos central."
    
    try:
        ws_historial = sh.worksheet("historial")
        ws_inventario = sh.worksheet("inventario")
        
        # Descargar el inventario actual para ubicar filas y stocks en tiempo real
        inv_data = ws_inventario.get_all_records()
        
        for item in canasta:
            # 1. Registrar el movimiento en la sábana histórica
            ws_historial.append_row([
                fecha, 
                tipo, 
                documento, 
                almacen, 
                item['Código'], 
                item['Material'], 
                item['Cantidad'], 
                item['Unidad'], 
                solicitante, 
                usuario, 
                obs
            ])
            
            # 2. Buscar la combinación de Almacén + Código de Material en la hoja de inventario
            fila_encontrada = None
            stock_actual = 0
            
            for idx, row in enumerate(inv_data):
                if str(row['Almacén']).strip() == str(almacen).strip() and str(row['Código']).strip() == str(item['Código']).strip():
                    fila_encontrada = idx + 2  # +2 por índice base 0 y fila de encabezados en Sheets
                    stock_actual = int(row['Stock']) if row['Stock'] != "" else 0
                    break
            
            # 3. Aplicar las matemáticas según tu flujo operacional solicitado
            # Ingresos y Devoluciones suman stock; Egresos restan stock
            if "Ingreso" in tipo or "Devolución" in tipo:
                nuevo_stock = stock_actual + int(item['Cantidad'])
            else:  # Egreso (Vale de Salida)
                nuevo_stock = max(0, stock_actual - int(item['Cantidad']))
                
            # 4. Impactar la celda correspondiente en la nube (Columna E = Número 5)
            if fila_encontrada:
                ws_inventario.update_cell(fila_encontrada, 5, nuevo_stock)
            else:
                # Si la combinación Almacén - Material no existía previamente, se crea la fila inicial
                ws_inventario.append_row([almacen, item['Código'], item['Material'], "Ubicación General", nuevo_stock])
                
        return True, "Transacción completada con éxito. Inventarios actualizados en la nube."
    except Exception as e:
        return False, f"Error crítico al procesar la transacción: {e}"

def guardar_foto_drive(archivo, almacen, usuario):
    """
    Registra metadatos de las imágenes de inspección por almacén.
    Almacena el enlace de acceso directo en la pestaña 'fotos'.
    """
    try:
        sh = conectar_sheets()
        if not sh:
            return None
            
        ws_fotos = sh.worksheet("fotos")
        
        # Enlace de tu carpeta real compartida en Google Drive donde subes las capturas
        enlace_drive_carpeta = "https://drive.google.com/drive/folders/tu_id_de_carpeta_compartida"
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Insertar registro persistente en Google Sheets para auditoría visual
        ws_fotos.append_row([fecha_str, almacen, usuario, enlace_drive_carpeta])
        return enlace_drive_carpeta
    except Exception as e:
        st.error(f"Error al escribir metadatos de la imagen en la nube: {e}")
        return None
