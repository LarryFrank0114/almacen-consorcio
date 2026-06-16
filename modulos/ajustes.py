import streamlit as st
import pandas as pd
import database as db

def render(sh):
    st.markdown("### Ajustes y Catálogos Técnicos")
    st.markdown("---")
    
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso Denegado: Esta sección requiere privilegios de Administrador para realizar modificaciones.")
        return

    # CONTROL DE SEGURIDAD: Inicializar el maestro si no existe en la sesión
    if "maestro_materiales" not in st.session_state or st.session_state.maestro_materiales is None:
        try:
            ws_maestro = sh.worksheet("maestro")
            st.session_state.maestro_materiales = pd.DataFrame(ws_maestro.get_all_records())
        except Exception as e:
            st.error(f"⚠️ No se pudo cargar el Catálogo Maestro desde Google Sheets: {e}")
            return

    # Formulario para registrar altas de material técnico
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
                st.error("❌ Todos los campos son obligatorios para el registro técnico.")
            else:
                exito, msg = db.agregar_material_maestro(nuevo_codigo, nueva_desc, nueva_unidad)
                if exito:
                    st.success(msg)
                    # Forzamos la actualización inmediata leyendo de nuevo el Google Sheet
                    try:
                        ws_maestro = sh.worksheet("maestro")
                        st.session_state.maestro_materiales = pd.DataFrame(ws_maestro.get_all_records())
                    except:
                        pass
                    st.rerun()
                else:
                    st.error(msg)
                    
    st.markdown("##### **Catálogo Central Vigilado Actual**")
    
    # Desplegar el dataframe de forma segura asegurando que no arroje error visual
    if not st.session_state.maestro_materiales.empty:
        st.dataframe(
            st.session_state.maestro_materiales, 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("ℹ️ No hay materiales registrados actualmente en el catálogo maestro.")
