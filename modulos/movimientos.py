import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

def render(sh):
    st.markdown("### Formulario de Registro de Movimientos Transaccionales")
    st.markdown("---")
    
    # 🔓 CONTROL DE ACCESO: Todos los usuarios autenticados pueden registrar movimientos
    if not st.session_state.get("logged_in", False):
        st.error("🚫 Inicie sesión para acceder a este módulo.")
        return

    # Forzar carga segura del maestro de materiales si no está en caché
    if "maestro_materiales" not in st.session_state or st.session_state.maestro_materiales is None:
        try:
            ws_maestro = sh.worksheet("maestro")
            st.session_state.maestro_materiales = pd.DataFrame(ws_maestro.get_all_records())
        except Exception as e:
            st.error(f"⚠️ No se pudo leer el catálogo maestro de materiales: {e}")
            return

    df_maestro = st.session_state.maestro_materiales

    if df_maestro.empty:
        st.warning("⚠️ El catálogo maestro de materiales está vacío. Por favor, registre materiales en Ajustes primero.")
        return

    # 🔐 FILTRADO RESTRINGIDO DE OPERACIÓN SEGÚN LA IDENTIDAD DEL USUARIO
    user = st.session_state.username
    
    if "Piero Pezo" in user:
        options_almacen = ["Almacén 10"]
    elif "Marcial Huayta" in user:
        options_almacen = ["Almacén 8"]
    elif "Enrique Sanchez" in user:
        options_almacen = ["Almacén 6"]
    elif "Gregorio Rodriguez" in user:
        options_almacen = ["Almacén 1"]
    else:
        # Larry y Supervisión tienen el control total de todas las sedes
        options_almacen = ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"]

    # ==========================================
    # FORMULARIO DE CABECERA LOGÍSTICA
    # ==========================================
    with st.form("form_cabecera_movs"):
        col1, col2 = st.columns(2)
        with col1:
            # Tipos de operaciones oficiales estandarizadas
            tipo_mov = st.selectbox("Tipo de Operación Logística:", [
                "Ingreso (Guía de Remisión)", 
                "Ingreso (Vale de Ingreso - Devolución)",
                "Egreso (Vale de Salida)"
            ])
            almacen_sel = st.selectbox("Almacén de Operación:", options=options_almacen)
        with col2:
            num_doc = st.text_input("Número de Documento Oficial (Guía / Vale):")
            fecha_sel = st.date_input("Fecha de Ejecución:", value=datetime.now().date())
            
        solicitante = st.text_input("Solicitante / Contratista / Cuadrilla Receptor:")
        observaciones = st.text_area("Notas Técnicas / Destino del Material:")
        
        # Botón obligatorio del formulario de cabecera
        st.form_submit_button("Fijar Datos de Cabecera")

    # Inicializar canasta si no existe
    if "canasta" not in st.session_state:
        st.session_state.canasta = []

    st.markdown("---")
    st.markdown("#### 🛒 Agregar Insumos al Documento Abierto")
    
    # 🛠️ ADAPTACIÓN DE COLUMNAS REALES (CODIGO y PRODUCTO)
    # Convertimos a string de manera segura para el combo selector
    opciones_combo = df_maestro['CODIGO'].astype(str) + " - " + df_maestro['PRODUCTO'].astype(str)
    
    col_mat1, col_mat2 = st.columns([3, 1])
    with col_mat1:
        seleccion_combo = st.selectbox("Seleccione el Material Técnico:", options=opciones_combo)
    with col_mat2:
        cantidad_item = st.number_input("Cantidad de Artículos:", min_value=1, value=1)

    if st.button("➕ Añadir Material a la Lista", use_container_width=True):
        cod_item = seleccion_combo.split(" - ")[0]
        nom_item = seleccion_combo.split(" - ")[1]
        
        # Obtener unidad de medida del maestro de forma segura usando tus columnas reales
        fila_mat = df_maestro[df_maestro['CODIGO'].astype(str) == cod_item]
        uni_item = fila_mat['UNIDAD'].values[0] if not fila_mat.empty else "Und"
        
        st.session_state.canasta.append({
            "Código": cod_item, "Material": nom_item, "Cantidad": cantidad_item, "Unidad": uni_item
        })
        st.toast(f"📦 Añadido: {nom_item} ({cantidad_item} {uni_item})")

    # Renderizado y procesamiento de la canasta abierta
    if st.session_state.canasta:
        st.markdown("<br>📦 **Items Cargados en el Documento Actual**", unsafe_allow_html=True)
        df_canasta = pd.DataFrame(st.session_state.canasta)
        st.dataframe(df_canasta, use_container_width=True, hide_index=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🧼 Vaciar Lista Completa", use_container_width=True):
                st.session_state.canasta = []
                st.rerun()
        with col_btn2:
            if st.button("🚀 PROCESAR Y TRANSACCIONAR EN LA NUBE", type="primary", use_container_width=True):
                if not num_doc or not solicitante:
                    st.error("❌ Error: Los campos 'Número de Documento' y 'Solicitante' son obligatorios para procesar el flujo.")
                else:
                    # Enviar transacciones a database.py para afectar inventarios y escribir historial
                    exito, msg = db.registrar_transaccion_avanzada(
                        tipo_mov, num_doc, almacen_sel, str(fecha_sel), solicitante, user, observaciones, st.session_state.canasta
                    )
                    if exito:
                        st.success(f"✔️ {msg}")
                        st.session_state.canasta = []
                    else:
                        st.error(f"❌ {msg}")
