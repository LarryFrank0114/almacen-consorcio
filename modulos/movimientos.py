import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

def render(sh):
    st.markdown("### Formulario de Registro de Movimientos Transaccionales")
    st.markdown("---")
    
    # Filtro de seguridad: Solo los perfiles autorizados a modificar operan la canasta
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso Denegado: Tu perfil no tiene permisos de edición de flujo logístico.")
        return

    if "maestro_materiales" not in st.session_state or st.session_state.maestro_materiales is None:
        try:
            st.session_state.maestro_materiales = pd.DataFrame(sh.worksheet("maestro").get_all_records())
        except:
            st.error("No se pudo leer el catálogo maestro.")
            return

    df_maestro = st.session_state.maestro_materiales

    # RESTRICCIÓN DE OPERACIÓN DE ALMACÉN SEGÚN USUARIO
    user = st.session_state.username
    if "Piero Pezo" in user: options_almacen = ["Almacén 10"]
    elif "Marcial Huayta" in user: options_almacen = ["Almacén 8"]
    elif "Enrique Sanchez" in user: options_almacen = ["Almacén 6"]
    elif "Gregorio Rodriguez" in user: options_almacen = ["Almacén 1"]
    else: options_almacen = ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"]

    with st.form("form_cabecera_movs"):
        col1, col2 = st.columns(2)
        with col1:
            # 📝 INCLUSIÓN DE LOS TRES TIPOS DE MOVIMIENTOS REQUERIDOS
            tipo_mov = st.selectbox("Tipo de Operación:", [
                "Ingreso (Guía de remisión)", 
                "Egreso (Vale de salida)", 
                "Devolución (Ingreso con vale)"
            ])
            almacen_sel = st.selectbox("Almacén Destino/Origen:", options=options_almacen)
        with col2:
            num_doc = st.text_input("Número de Documento Oficial (Guía/Vale):")
            fecha_sel = st.date_input("Fecha de Ejecución:", value=datetime.now().date())
            
        solicitante = st.text_input("Solicitante / Contratista / Cuadrilla:")
        observaciones = st.text_area("Notas Técnicas de Campo:")
        st.form_submit_button("Fijar Datos de Cabecera")

    if "canasta" not in st.session_state:
        st.session_state.canasta = []

    st.markdown("---")
    st.markdown("#### 🛒 Agregar Insumos al Documento Abierto")
    
    opciones_combo = df_maestro['Código'].astype(str) + " - " + df_maestro['Material'].astype(str)
    col_mat1, col_mat2 = st.columns([3, 1])
    with col_mat1:
        seleccion_combo = st.selectbox("Seleccione Material:", options=opciones_combo)
    with col_mat2:
        cantidad_item = st.number_input("Cantidad a transaccionar:", min_value=1, value=1)

    if st.button("➕ Añadir Material a la Lista"):
        cod_item = seleccion_combo.split(" - ")[0]
        nom_item = seleccion_combo.split(" - ")[1]
        uni_item = df_maestro[df_maestro['Código'].astype(str) == cod_item]['Unidad'].values[0]
        
        st.session_state.canasta.append({
            "Código": cod_item, "Material": nom_item, "Cantidad": cantidad_item, "Unidad": uni_item
        })
        st.toast(f"Añadido: {nom_item}")

    if st.session_state.canasta:
        st.markdown("📦 **Items Cargados en el Documento Actual**")
        df_canasta = pd.DataFrame(st.session_state.canasta)
        st.dataframe(df_canasta, use_container_width=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🧼 Vaciar Lista"):
                st.session_state.canasta = []
                st.rerun()
        with col_btn2:
            if st.button("🚀 PROCESAR Y AFECTAR STOCKS", type="primary"):
                if not num_doc or not solicitante:
                    st.error("Por favor completa los campos obligatorios del documento.")
                else:
                    # Enviar a base de datos para registrar transacciones y recalcular inventario
                    exito, msg = db.registrar_transaccion_avanzada(
                        tipo_mov, num_doc, almacen_sel, str(fecha_sel), solicitante, user, observaciones, st.session_state.canasta
                    )
                    if exito:
                        st.success(msg)
                        st.session_state.canasta = []
                    else:
                        st.error(msg)
