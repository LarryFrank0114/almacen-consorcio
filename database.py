import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def conectar_sheets():
    """ Establece la conexión segura con Google Sheets usando las credenciales TOML """
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
    """ Registra los ingresos/egresos en el Historial y altera el Stock en el Inventario """
    sh = conectar_sheets()
    if not sh: 
        return False, "Sin conexión con la base de datos central."
    
    try:
        ws_historial = sh.worksheet("historial")
        ws_inventario = sh.worksheet("inventario")
        inv_data = ws_inventario.get_all_records()
        
        for item in canasta:
            ws_historial.append_row([
                fecha, tipo, documento, almacen, item['Código'], 
                item['Material'], item['Cantidad'], item['Unidad'], 
                solicitante, usuario, obs
            ])
            
            fila_encontrada = None
            stock_actual = 0
            
            for idx, row in enumerate(inv_data):
                if str(row['Almacén']).strip() == str(almacen).strip() and str(row['Código']).strip() == str(item['Código']).strip():
                    fila_encontrada = idx + 2
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

def modificar_material_maestro(codigo_material, nuevo_nombre, nueva_unidad):
    """ CRUD: Actualiza el nombre o unidad de un material en la pestaña 'maestro' """
    sh = conectar_sheets()
    if not sh: 
        return False, "Sin conexión con la base de datos."
    try:
        ws_maestro = sh.worksheet("maestro")
        data = ws_maestro.get_all_records()
        
        for idx, row in enumerate(data):
            if str(row['Código']).strip() == str(codigo_material).strip():
                fila_a_editar = idx + 2
                ws_maestro.update_cell(fila_a_editar, 2, nuevo_nombre)
                ws_maestro.update_cell(fila_a_editar, 3, nueva_unidad)
                return True, "Material modificado correctamente en la base de datos."
        return False, "No se encontró el código del material solicitado."
    except Exception as e:
        return False, f"Error al intentar modificar: {e}"

def eliminar_material_maestro(codigo_material):
    """ CRUD: Elimina físicamente la fila de un material en la pestaña 'maestro' """
    sh = conectar_sheets()
    if not sh: 
        return False, "Sin conexión con la base de datos."
    try:
        ws_maestro = sh.worksheet("maestro")
        data = ws_maestro.get_all_records()
        
        for idx, row in enumerate(data):
            if str(row['Código']).strip() == str(codigo_material).strip():
                fila_a_borrar = idx + 2 
                ws_maestro.delete_rows(fila_a_borrar)
                return True, "El material ha sido eliminado del catálogo maestro."
        return False, "No se encontró el código del material a eliminar."
    except Exception as e:
        return False, f"Error al intentar eliminar: {e}"

def guardar_foto_drive(archivo, almacen, usuario):
    """ Registra la trazabilidad de las auditorías fotográficas en la pestaña 'fotos' """
    try:
        sh = conectar_sheets()
        if not sh: return None
        ws_fotos = sh.worksheet("fotos")
        enlace_drive_carpeta = "https://drive.google.com/drive/folders/12MLYN3FNhEnw3gjRAuphepLWWDccoBDc?usp=sharing"
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws_fotos.append_row([fecha_str, almacen, usuario, enlace_drive_carpeta])
        return enlace_drive_carpeta
    except Exception as e:
        st.error(f"Error al escribir metadatos de la imagen en la nube: {e}")
        return None
