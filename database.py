import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def conectar_sheets():
    """
    Establece la conexión centralizada con Google Sheets utilizando las credenciales de GCP.
    Esta es la función que app.py necesita encontrar en la línea 71.
    """
    try:
        # Configuración de los permisos de lectura y escritura en Google Drive y Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lee las credenciales del bloque estructurado [gcp_service_account] en tus Secrets
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        else:
            creds_dict = dict(st.secrets)
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Nombre del archivo excel en tu Google Drive
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
            # Registrar cada línea en el historial general
            ws_historial.append_row([fecha, tipo, documento, almacen, item['Código'], item['Material'], item['Cantidad'], solicitante, usuario, obs])
            
            # Buscar coincidencia exacta en la hoja de inventarios consolidados
            fila_encontrada = None
            stock_actual = 0
            for idx, row in enumerate(inv_data, start=2):
                if str(row.get('Almacén', '')).strip() == str(almacen).strip() and str(row.get('Código', '')).strip() == str(item['Código']).strip():
                    fila_encontrada = idx
                    stock_actual = int(row['Stock']) if row['Stock'] != "" else 0
                    break
            
            # Calcular el nuevo inventario según la operación
            if "Ingreso" in tipo or "Devolución" in tipo:
                nuevo_stock = stock_actual + int(item['Cantidad'])
            else:
                nuevo_stock = max(0, stock_actual - int(item['Cantidad']))
                
            # Actualizar fila existente o crear una nueva si es un material nuevo en el almacén
            if fila_encontrada:
                ws_inventario.update_cell(fila_encontrada, 5, nuevo_stock)
            else:
                ws_inventario.append_row([almacen, item['Código'], item['Material'], "Ubicación General", nuevo_stock])
                
        return True, "Transacción completada con éxito. Inventarios updated en la nube."
    except Exception as e:
        return False, f"Error crítico al procesar la transacción: {e}"

def agregar_material_maestro(codigo, descripcion, unidad):
    try:
        sh = conectar_sheets()
        if not sh: return False, "Fallo de comunicación con la base de datos."
        ws_maestro = sh.worksheet("maestro")
        
        # Validar si ya existe el código
        codigos_existentes = ws_maestro.col_values(1)
        if str(codigo).strip() in [str(c).strip() for c in codigos_existentes]:
            return False, f"⚠️ El código '{codigo}' ya se encuentra registrado en el maestro central."
            
        ws_maestro.append_row([str(codigo).strip(), str(descripcion).strip(), unidad])
        return True, f"✔️ Material {descripcion} dado de alta con éxito."
    except Exception as e:
        return False, f"Error técnico: {e}"

def guardar_foto_drive(archivo, almacen, usuario):
    """
    Sube el archivo físico directamente a Google Drive utilizando las mismas credenciales,
    evitando el límite de caracteres de celdas en Sheets.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        else:
            creds_dict = dict(st.secrets)
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        # Librerías de Google API cargadas internamente de forma dinámica
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        import io
        
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Configurar metadatos del archivo a subir
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nombre_archivo = f"Inspeccion_{almacen.replace(' ', '_')}_{fecha_str}.jpg"
        
        file_metadata = {'name': nombre_archivo}
        
        # Preparar los bytes binarios de la imagen
        bytes_data = archivo.getvalue()
        fh = io.BytesIO(bytes_data)
        formato_imagen = archivo.type if hasattr(archivo, 'type') else "image/jpeg"
        
        media = MediaIoBaseUpload(fh, mimetype=formato_imagen, resumable=True)
        
        # Subir física al Drive
        archivo_subido = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = archivo_subido.get('id')
        
        # Permiso público de lectura automática para que la app lo cargue en el mosaico
        user_permission = {'type': 'anyone', 'role': 'reader'}
        drive_service.permissions().create(fileId=file_id, body=user_permission).execute()
        
        # URL directa que Streamlit procesa a la perfección
        enlace_directo = f"https://lh3.googleusercontent.com/u/0/d/{file_id}"
        
        # Registrar el enlace en la pestaña 'fotos' de Google Sheets
        sh = conectar_sheets()
        if not sh: return None
        
        lista_hojas = [h.title for h in sh.worksheets()]
        if "fotos" not in lista_hojas:
            ws_fotos = sh.add_worksheet(title="fotos", rows="1000", cols="4")
            ws_fotos.append_row(["Fecha", "Almacen", "Usuario", "Enlace"])
        else:
            ws_fotos = sh.worksheet("fotos")
            
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws_fotos.append_row([fecha_registro, almacen, usuario, enlace_directo])
        
        return enlace_directo
        
    except Exception as e:
        st.error(f"Error al subir archivo a la nube e indexar: {e}")
        return None
