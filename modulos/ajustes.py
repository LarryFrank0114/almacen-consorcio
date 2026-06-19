import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

def render(sh):
    st.markdown("### Ajustes y Catálogos Técnicos")
    st.markdown("---")
    
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso Denegado: Esta sección requiere privilegios de Administrador para realizar modificaciones.")
        return

    if "maestro_materiales" not in st.session_state or st.session_state.maestro_materiales is None:
        try:
            lista_hojas = [h.title for h in sh.worksheets()]
            hoja_maestro_real = next((h for h in lista_hojas if h.strip().lower() == "maestro"), "maestro")
            ws_maestro = sh.worksheet(hoja_maestro_real)
            st.session_state.maestro_materiales = pd.DataFrame(ws_maestro.get_all_records())
        except Exception as e:
            st.error(f"⚠️ No se pudo cargar el Catálogo Maestro: {e}")
            return

    # Formulario 1: Alta de Materiales
    st.markdown("#### 🛠️ Registro de Alta de Materiales")
    with st.form("form_alta_material", clear_on_submit=True):
        col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
        with col_m1:
            nuevo_codigo = st.text_input("Código de Inventario Único:")
        with col_m2:
            nueva_desc = st.text_input("Descripción Completa:")
        with col_m3:
            nueva_unidad = st.selectbox("Unidad Oficial:", ["Metros", "Unidades", "Varillas", "Planchas", "Kilos", "Galones", "Rollos"])
            
        alta_presionada = st.form_submit_button("Registrar Alta de Material")
        if alta_presionada:
            if not nuevo_codigo or not nueva_desc:
                st.error("❌ Todos los campos son obligatorios.")
            else:
                exito, msg = db.agregar_material_maestro(nuevo_codigo, nueva_desc, nueva_unidad)
                if exito:
                    st.success(msg)
                    try:
                        ws_maestro = sh.worksheet("maestro")
                        st.session_state.maestro_materiales = pd.DataFrame(ws_maestro.get_all_records())
                    except:
                        pass
                    st.rerun()
                else:
                    st.error(msg)

    # Formulario 2: Configuración de Ubicación e Infraestructura
    st.markdown("---")
    st.markdown("#### 📍 Configuración de Infraestructura y Ubicaciones de Almacén")
    
    almacenes_sistema = ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"]
    
    with st.form("form_config_ubicacion", clear_on_submit=True):
        almacen_geo = st.selectbox("Seleccione el Almacén a Parametrizar:", options=almacenes_sistema)
        coordenadas_url = st.text_input("Ubicación (Enlace de Google Maps o Coordenadas GPS Lat, Lon):", placeholder="Ejemplo: -11.9842, -77.1204")
        referencias_text = st.text_area("Referencias Físicas de Acceso:")
        foto_almacen_file = st.file_uploader("Imagen Oficial de Fachada:", type=["png", "jpg", "jpeg"])
        
        guardar_geo = st.form_submit_button("💾 Guardar Configuración de Sede")
        
        if guardar_geo:
            if not coordenadas_url or not referencias_text:
                st.warning("⚠️ La ubicación y las referencias son obligatorias.")
            else:
                try:
                    lista_hojas = [h.title for h in sh.worksheets()]
                    if "ubicaciones" not in lista_hojas:
                        ws_ub = sh.add_worksheet(title="ubicaciones", rows="500", cols="6")
                        ws_ub.append_row(["Fecha", "Almacen", "Ubicacion", "Referencias", "Enlace_Foto", "Configurado_Por"])
                    else:
                        ws_ub = sh.worksheet("ubicaciones")
                    
                    enlace_foto_drive = ""
                    if foto_almacen_file is not None:
                        enlace_foto_drive = db.guardar_foto_drive(foto_almacen_file, almacen_geo, st.session_state.username)
                    
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                    ws_ub.append_row([fecha_actual, almacen_geo, coordenadas_url, referencias_text, enlace_foto_drive if enlace_foto_drive else "", st.session_state.username])
                    st.success(f"✔️ Infraestructura guardada para el {almacen_geo}.")
                except Exception as e:
                    st.error(f"Error al escribir ubicación en Sheets: {e}")

    st.markdown("<br>##### **Catálogo Central Vigilado Actual**")
    if not st.session_state.maestro_materiales.empty:
        st.dataframe(st.session_state.maestro_materiales, use_container_width=True, hide_index=True)
