import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # 🛠️ Corrección de compatibilidad: Intenta usar la clave antigua o la estructura directa de tus secrets anteriores
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
        elif "gspread_credentials" in st.secrets:
            creds_dict = st.secrets["gspread_credentials"]
        else:
            # Si tus secretos están guardados de forma directa en la raíz del TOML de Streamlit
            creds_dict = dict(st.secrets)
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Asegúrate de que este nombre corresponda exactamente al de tu archivo en Google Drive
        return client.open("01 - Herramientas") 
    except Exception as e:
        st.error(f"Error de conexión GCP: {e}")
        return None
def registrar_transaccion_avanzada(tipo, documento, almacen, fecha, solicitante, usuario, obs, canasta):
    sh = conectar_sheets()
    if not sh: return False, "Sin conexión."
    
    try:
        ws_historial = sh.worksheet("historial")
        ws_inventario = sh.worksheet("inventario")
        
        # Cargar inventario actual para modificar unidades en caliente
        inv_data = ws_inventario.get_all_records()
        
        for item in canasta:
            # 1. Registrar fila en el Historial General
            ws_historial.append_row([
                fecha, tipo, documento, almacen, item['Código'], item['Material'], item['Cantidad'], item['Unidad'], solicitante, usuario, obs
            ])
            
            # 2. Modificar el stock en la pestaña "inventario"
            fila_encontrada = None
            stock_actual = 0
            
            for idx, row in enumerate(inv_data):
                if str(row['Almacén']) == almacen and str(row['Código']) == str(item['Código']):
                    fila_encontrada = idx + 2 # +2 por índice base 0 y encabezado
                    stock_actual = int(row['Stock'])
                    break
            
            # Calcular afectación numérica
            if "Ingreso" in tipo or "Devolución" in tipo:
                nuevo_stock = stock_actual + int(item['Cantidad'])
            else: # Egreso
                nuevo_stock = max(0, stock_actual - int(item['Cantidad']))
                
            if fila_encontrada:
                # Actualizar columna E (Stock) que es la número 5
                ws_inventario.update_cell(fila_encontrada, 5, nuevo_stock)
                
        return True, "Transacción completada. Inventarios recalculados en la nube."
    except Exception as e:
        return False, f"Error en procesamiento: {e}"

def guardar_foto_drive(archivo, almacen, usuario):
    # Simula la subida al repositorio de imágenes o Drive y genera el enlace público de visualización.
    # Para usar producción real de Drive se requiere habilitar la Drive API en tu consola GCP.
    try:
        sh = conectar_sheets()
        ws_fotos = sh.worksheet("fotos")
        
        # Enlace simulado o real (puedes parametrizarlo con tu carpeta de Drive compartida)
        enlace_estatico = f"https://drive.google.com/drive/folders/tu_id_de_carpeta_compartida"
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Registrar metadatos en Google Sheets para que no se pierdan nunca
        ws_fotos.append_row([fecha_str, almacen, usuario, enlace_estatico])
        return enlace_estatico
    except Exception as e:
        st.error(f"Error al escribir metadatos de imagen: {e}")
        return None
