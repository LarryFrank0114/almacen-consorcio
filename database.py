import streamlit as st
import pandas as pd
import gspread

def conectar_sheets():
    """Establece conexión con la hoja de cálculo usando el JSON directo de los secretos."""
    try:
        import json
        # Leemos el JSON completo estructurado directamente desde los secretos
        credenciales_dict = json.loads(st.secrets["google_sheets_json"])
        gc = gspread.service_account_from_dict(credenciales_dict)
        
        # Abrir el libro por su nombre exacto
        sh = gc.open("Inventario Consorcio San Miguel")
        return sh
    except Exception as e:
        st.error(f"❌ Error de conexión con Google Sheets: {e}")
        return None

def inicializar_db():
    """Extrae el inventario real desde Google Sheets y lo monta en la sesión actual."""
    sh = conectar_sheets()
    if sh is not None:
        try:
            # Obtener datos de la pestaña 'inventario'
            worksheet = sh.worksheet("inventario")
            datos = worksheet.get_all_records()
            
            # Cargar a session_state como DataFrame nativo
            if datos:
                st.session_state.inventario = pd.DataFrame(datos)
            else:
                # Si la hoja está vacía, estructurarla con columnas por defecto
                st.session_state.inventario = pd.DataFrame(columns=["Código", "Material", "Almacén", "Ubicación", "Stock", "Unidad", "Encargado"])
        except Exception as e:
            st.error(f"Error al leer la pestaña 'inventario': {e}")
            st.session_state.inventario = pd.DataFrame(columns=["Código", "Material", "Almacén", "Ubicación", "Stock", "Unidad", "Encargado"])
    else:
        if 'inventario' not in st.session_state:
            st.session_state.inventario = pd.DataFrame(columns=["Código", "Material", "Almacén", "Ubicación", "Stock", "Unidad", "Encargado"])

    # Estructura del maestro auxiliar y de movimientos transaccionales en caché temporal
    if 'maestro_materiales' not in st.session_state:
        st.session_state.maestro_materiales = pd.DataFrame([
            {"Código": "TUB-PE-110", "Material": "Tubería PEAD 110mm", "Unidad": "Metros"},
            {"Código": "VAL-CO-04", "Material": "Válvula de Compuerta de 4 Pulgadas", "Unidad": "Unidades"},
            {"Código": "ACC-TEE-110", "Material": "Accesorio Tee Inyectada 110mm", "Unidad": "Unidades"}
        ])

    if 'historial_movimientos' not in st.session_state:
        st.session_state.historial_movimientos = pd.DataFrame(columns=[
            "Fecha", "Tipo", "Documento", "Almacén", "Solicitante", "Supervisor", "Código", "Material", "Cantidad", "Unidad", "Encargado", "Observaciones"
        ])

def sincronizar_a_google_sheets(df):
    """Sobrescribe la pestaña de Google Sheets para mantener la persistencia ante reinicios."""
    sh = conectar_sheets()
    if sh is not None:
        try:
            worksheet = sh.worksheet("inventario")
            worksheet.clear()  # Limpiar datos antiguos
            
            # Preparar encabezados y filas
            encabezados = df.columns.tolist()
            valores = df.values.tolist()
            
            # Insertar todo en una sola transacción eficiente hacia la API de Google
            worksheet.update([encabezados] + valores)
            return True
        except Exception as e:
            st.error(f"❌ No se pudo sincronizar a Google Sheets: {e}")
            return False
    return False

def registrar_transaccion(tipo_mov, doc, almacen, fecha, solicitante, supervisor, encargado, observaciones, lista_recursos):
    """Procesa los movimientos modificando el stock en memoria y enviando los cambios de forma síncrona a Google Sheets."""
    df_inv = st.session_state.inventario
    df_hist = st.session_state.historial_movimientos
    nuevos_movimientos = []

    if tipo_mov == "Egreso (Vale de Salida)":
        for rec in lista_recursos:
            idx = df_inv[(df_inv['Código'] == rec['Código']) & (df_inv['Almacén'] == almacen)].index
            stock_actual = df_inv.at[idx[0], 'Stock'] if len(idx) > 0 else 0
            if stock_actual < rec['Cantidad']:
                return False, f"❌ Stock insuficiente de {rec['Material']} en {almacen}. Disponible: {stock_actual}"

    for rec in lista_recursos:
        idx = df_inv[(df_inv['Código'] == rec['Código']) & (df_inv['Almacén'] == almacen)].index
        
        if len(idx) > 0:
            stock_actual = int(df_inv.at[idx[0], 'Stock'])
            if tipo_mov == "Egreso (Vale de Salida)":
                df_inv.at[idx[0], 'Stock'] = stock_actual - rec['Cantidad']
            else:
                df_inv.at[idx[0], 'Stock'] = stock_actual + rec['Cantidad']
        else:
            nuevo_stock_item = {
                "Código": rec['Código'], "Material": rec['Material'], "Almacén": almacen,
                "Ubicación": "Por Asignar", "Stock": rec['Cantidad'], "Unidad": rec['Unidad'], "Encargado": encargado
            }
            df_inv = pd.concat([df_inv, pd.DataFrame([nuevo_stock_item])], ignore_index=True)

        mov = {
            "Fecha": str(fecha), "Tipo": tipo_mov, "Documento": doc, "Almacén": almacen,
            "Solicitante": solicitante, "Supervisor": supervisor, "Código": rec['Código'],
            "Material": rec['Material'], "Cantidad": rec['Cantidad'], "Unidad": rec['Unidad'],
            "Encargado": encargado, "Observaciones": observaciones
        }
        nuevos_movimientos.append(mov)

    # Actualizar estados internos
    st.session_state.inventario = df_inv
    st.session_state.historial_movimientos = pd.concat([df_hist, pd.DataFrame(nuevos_movimientos)], ignore_index=True)
    
    # 💾 IMPACTAR LA BASE DE DATOS EN LA NUBE INMEDIATAMENTE
    sincronizar_a_google_sheets(df_inv)
    
    return True, f"✔️ Transacción {doc} procesada y guardada en Google Sheets con éxito."
