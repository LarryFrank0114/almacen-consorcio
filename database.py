import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64

# ... [Mantiene las funciones conectar_sheets y registrar_transaccion_avanzada intactas] ...

def guardar_foto_drive(archivo, almacen, usuario):
    """
    Procesa la imagen para precaver errores 404 convirtiendo la captura de Streamlit 
    en una cadena Base64 segura que se almacena directamente en Google Sheets y se visualiza en la nube sin enlaces caídos.
    """
    try:
        sh = conectar_sheets()
        if not sh: return None
        
        # Verificar o crear la pestaña de fotos
        lista_hojas = [h.title for h in sh.worksheets()]
        if "fotos" not in lista_hojas:
            ws_fotos = sh.add_worksheet(title="fotos", rows="500", cols="4")
            ws_fotos.append_row(["Fecha", "Almacen", "Usuario", "Enlace"])
        else:
            ws_fotos = sh.worksheet("fotos")
            
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # SOLUCIÓN AL ERROR 404: Convertimos el archivo cargado a Base64
        # Esto permite almacenar la imagen directamente en la celda y renderizarla nativamente sin servidores intermedios rotos
        bytes_data = archivo.getvalue()
        base64_encoded = base64.b64encode(bytes_data).decode('utf-8')
        formato_imagen = archivo.type if hasattr(archivo, 'type') else "image/jpeg"
        data_uri = f"data:{formato_imagen};base64,{base64_encoded}"
        
        # Guardar la fila con la Data URI segura en la columna Enlace
        ws_fotos.append_row([fecha_str, almacen, usuario, data_uri])
        return data_uri
    except Exception as e:
        st.error(f"Error al guardar e inmortalizar fotografía en la base central: {e}")
        return None
