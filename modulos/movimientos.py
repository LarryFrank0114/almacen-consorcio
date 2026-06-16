import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

def render(sh):
    st.markdown("### Registro de Movimientos")
    st.markdown("---")
    
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso Denegado: Los usuarios de Supervisión externa no están autorizados a emitir movimientos.")
        return

    with st.form("form_cabecera"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            tipo_mov = st.selectbox("Tipo Logístico:", ["Ingreso (Guía de Remisión)", "Egreso (Vale de Salida)"])
            almacen_sel = st.selectbox("Almacén de Operación:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
        with col_c2:
            num_doc = st.text_input("Número de Documento Oficial")
            fecha_sel = st.date_input("Fecha", value=datetime.now().date())
            
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            solicitante = st.text_input("Solicitante / Cuadrilla:")
        with col_p2:
            supervisor = st.text_input("Ing. Supervisor / Residente:")
            
        observaciones = st.text_area("Observaciones del Destino:")
        st.form_submit_button("Confirmar Cabecera")
        
    if "canasta" not in st.session_state:
        st.session_state.canasta = []
        
    st.markdown("---")
    st.markdown("##### **Agregar Insumos al Documento Abierto**")
    df_maestro = st.session_state.maestro_materiales
    col_mat1, col_mat2 = st.columns([3, 1])
    with col_mat1:
        seleccion_combo = st.selectbox("Material Técnico:", options=df_maestro['Código'] + " - " + df_maestro['Material'])
    with col_mat2:
        cantidad_item = st.number_input("Cantidad:", min_value=1, value=1)
        
    if st.button("➕ Añadir a la lista", use_container_width=True):
        cod_item = seleccion_combo.split(" - ")[0]
        nom_item = seleccion_combo.split(" - ")[1]
        uni_item = df_maestro[df_maestro['Código'] == cod_item]['Unidad'].values[0]
        
        st.session_state.canasta.append({
            "Código": cod_item, "Material": nom_item, "Cantidad": cantidad_item, "Unidad": uni_item
        })
        st.toast(f"Agregado: {nom_item}")
        
    if st.session_state.canasta:
        st.markdown("#### Items a Procesar")
        df_canasta = pd.DataFrame(st.session_state.canasta)
        st.dataframe(df_canasta, use_container_width=True)
        
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            if st.button("🧼 Vaciar Todo", use_container_width=True):
                st.session_state.canasta = []
                st.rerun()
        with col_acc2:
            if st.button("🚀 ENVIAR TRANSACCIÓN A GOOGLE SHEETS", type="primary", use_container_width=True):
                if not num_doc or not solicitante or not supervisor:
                    st.error("❌ Faltan datos obligatorios en la cabecera.")
                else:
                    exito, msg = db.registrar_transaccion(
                        tipo_mov, num_doc, almacen_sel, fecha_sel, solicitante, supervisor, st.session_state.username, observaciones, st.session_state.canasta
                    )
                    if exito:
                        st.success(msg)
                        st.session_state.canasta = []
                    else:
                        st.error(msg)
