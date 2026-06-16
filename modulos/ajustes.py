import streamlit as st
import pandas as pd

def render(sh):
    st.markdown("### Ajustes y Catálogos Técnicos")
    
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso Denegado: No tiene privilegios para alterar el Catálogo Maestro de Materiales.")
        return

    with st.form("form_nuevo_material"):
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            nuevo_cod = st.text_input("Código de Inventario Único:")
        with col_n2:
            nuevo_nom = st.text_input("Descripción Completa:")
        with col_n3:
            nueva_uni = st.selectbox("Unidad Oficial:", ["Metros", "Unidades", "Varillas", "Global"])
            
        if st.form_submit_button("💾 Registrar Alta de Material"):
            if nuevo_cod and nuevo_nom:
                nuevo_row = {"Código": nuevo_cod, "Material": nuevo_nom, "Unidad": nueva_uni}
                st.session_state.maestro_materiales = pd.concat([st.session_state.maestro_materiales, pd.DataFrame([nuevo_row])], ignore_index=True)
                st.success("✔️ Insumo agregado de forma exitosa.")
            else:
                st.error("❌ Complete los campos obligatorios.")
                
    st.dataframe(st.session_state.maestro_materiales, use_container_width=True, hide_index=True)
