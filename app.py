import streamlit as st
import pandas as pd
from datetime import datetime
import database as db  # Conexión con nuestro módulo de Google Sheets

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y SESIÓN
# ==========================================
st.set_page_config(
    page_title="Sistema de Gestión de Almacenes - Consorcio San Miguel",
    page_icon="📦",
    layout="wide"
)

# Inicializar estados de sesión para control de login
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "rol_actual" not in st.session_state:
    st.session_state.rol_actual = None

# Cargar catálogo maestro si no existe en sesión (Módulo 4)
if "maestro_materiales" not in st.session_state:
    st.session_state.maestro_materiales = pd.DataFrame([
        {"Código": "HID-PO-01", "Material": "Tubo Polietileno 110mm Pn10", "Unidad": "Metros"},
        {"Código": "ACC-CR-05", "Material": "Cruceta de Hierro Fundido DN 100", "Unidad": "Unidades"},
        {"Código": "VAL-CO-02", "Material": "Válvula de Compuerta C/Brida 4\"", "Unidad": "Unidades"}
    ])

# Conectar a la base de datos de Google Sheets
sh = db.conectar_sheets()

if sh is None:
    st.error("❌ No se pudo establecer la comunicación con el servidor central de Google Sheets. Verifique la configuración de Secrets.")
    st.stop()

# ==========================================
# PANTALLA DE CONTROL DE ACCESO (LOGIN)
# ==========================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 CONTROL DE ACCESO LOGÍSTICO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Megaproyecto Sectorial Saneamiento 'Nueva Rinconada'</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("formulario_login"):
            usuario = st.text_input("Usuario")
            contrasena = st.text_input("Contraseña", type="password")
            btn_ingresar = st.form_submit_button("Iniciar Sesión")
            
            if btn_ingresar:
                if usuario.lower() == "larry" and contrasena == "admin123":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Larry Frank Rodriguez"
                    st.session_state.rol_actual = "Jefe de Almacenes"
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Intente nuevamente.")
    st.stop()

# ==========================================
# ESTRUCTURA PRINCIPAL (SIDEBAR - MENÚ)
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.usuario_actual}")
    st.markdown(f"**Rol:** {st.session_state.rol_actual}")
    st.markdown("<span style='color:green;'>● Conectado a Google Sheets</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📌 MENÚ DE OPERACIONES")
    opcion_menu = st.radio(
        "Seleccione un módulo:",
        [
            "📊 Dashboard Gerencial",
            "📖 Reporte de Stock Actual",
            "🔄 Registrar Movimiento (Guías/Vales)",
            "⚙️ Configurar Almacenes (1, 6, 8, 10)"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 Salir del Sistema"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.session_state.rol_actual = None
        st.rerun()

# ==========================================
# MÓDULO 1: DASHBOARD GERENCIAL
# ==========================================
if opcion_menu == "📊 Dashboard Gerencial":
    st.markdown("# 📊 DASHBOARD CORPORATIVO DE MOVIMIENTOS")
    st.markdown("---")
    
    try:
        ws_historial = sh.worksheet("historial")
        df_historial = pd.DataFrame(ws_historial.get_all_records())
    except Exception:
        df_historial = pd.DataFrame()
        
    if df_historial.empty:
        st.info("No se registran movimientos transaccionales en el historial para generar gráficos.")
    else:
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.metric("Total Transacciones", len(df_historial))
        with col_kpi2:
            ingresos = len(df_historial[df_historial['Tipo'].str.contains('INGRESO', case=False, na=False)])
            st.metric("Total Ingresos (Guías)", ingresos)
        with col_kpi3:
            salidas = len(df_historial[df_historial['Tipo'].str.contains('SALIDA', case=False, na=False)])
            st.metric("Total Salidas (Vales)", salidas)
        
        st.markdown("### 📈 Historial Completo de Operaciones")
        st.dataframe(df_historial, use_container_width=True, hide_index=True)

# ==========================================
# MÓDULO 2: REPORTE DE STOCK ACTUAL (CRUD CORREGIDO)
# ==========================================
elif opcion_menu == "📖 Reporte de Stock Actual":
    st.markdown("# 📖 REPORTE DE STOCK CONSOLIDADO EN TIEMPO REAL")
    st.markdown("---")
    
    try:
        ws_inv = sh.worksheet("inventario")
        datos_inv = ws_inv.get_all_records()
        df_inv = pd.DataFrame(datos_inv)
    except Exception as e:
        st.error(f"Error al leer la pestaña 'inventario': {e}")
        st.stop()
        
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_almacen = st.multiselect("Filtrar por Sede / Almacén:", options=df_inv['Almacén'].unique(), default=df_inv['Almacén'].unique())
    with col_f2:
        buscar_material = st.text_input("🔍 Buscar material por descripción o código:")
        
    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar_material:
        df_filtrado = df_filtrado[
            df_filtrado['Material'].str.contains(buscar_material, case=False) | 
            df_filtrado['Código'].astype(str).str.contains(buscar_material, case=False)
        ]
        
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    st.markdown("### 📥 Panel de Descargas de Reportes Oficiales")
    csv = df_filtrado.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button("🟢 Descargar Reporte de Stock para EXCEL (.csv)", data=csv, file_name="stock_consorcio.csv", mime="text/csv")

    # 🛠️ SECCIÓN INTERNA: PANEL CRUD (CON TILDES SINCRO)
    st.markdown("---")
    st.markdown("### 🛠️ PANEL DE CORRECCIÓN LOGÍSTICA IN SITU")
    
    # Sincronizado con tilde exacta para hacer match con la base de datos
    almacen_crud_sel = st.selectbox("1. Seleccione Almacén del recurso a modificar:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
    materiales_en_almacen = df_inv[df_inv['Almacén'].astype(str) == almacen_crud_sel]
    
    if not materiales_en_almacen.empty:
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel2:
            opciones_combo = materiales_en_almacen['Código'].astype(str) + " - " + materiales_en_almacen['Material'].astype(str)
            material_crud = st.selectbox("2. Seleccione el Material a modificar:", options=opciones_combo, key="crud_material")
        
        codigo_seleccionado = material_crud.split(" - ")[0]
        datos_material = materiales_en_almacen[materiales_en_almacen['Código'].astype(str) == codigo_seleccionado].iloc[0]
        
        with st.form("form_edicion_rapida"):
            st.markdown(f"**Modificando artículo:** {datos_material['Material']} en **{almacen_crud_sel}**")
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                nuevo_stock = st.number_input("Stock Físico Real:", value=int(datos_material['Stock']), min_value=0)
            with col_e2:
                nueva_ubica = st.text_input("Nueva Ubicación Interna:", value=str(datos_material['Ubicación']))
            with col_e3:
                nuevo_encargado = st.text_input("Encargado de Custodia:", value=str(datos_material['Encargado']))
                
            btn_guardar_crud = st.form_submit_button("💾 Actualizar Ficha en Google Sheets")
            
            if btn_guardar_crud:
                todos_los_datos = ws_inv.get_all_records()
                fila_editar = None
                for idx, fila in enumerate(todos_los_datos):
                    if str(fila['Almacén']) == almacen_crud_sel and str(fila['Código']) == codigo_seleccionado:
                        fila_editar = idx + 2
                        break
                
                if fila_editar:
                    ws_inv.update_cell(fila_editar, 5, nuevo_stock)
                    ws_inv.update_cell(fila_editar, 4, nueva_ubica)
                    ws_inv.update_cell(fila_editar, 7, nuevo_encargado)
                    st.success("✔️ Google Sheets actualizado con éxito. Recargando datos...")
                    st.rerun()
                else:
                    st.error("❌ No se encontró el registro en la nube.")
    else:
        st.info("No se encontraron materiales registrados en la sede seleccionada.")

# ==========================================
# MÓDULO 3: REGISTRAR MOVIMIENTO (COMPLETO)
# ==========================================
elif opcion_menu == "🔄 Registrar Movimiento (Guías/Vales)":
    st.markdown("# 🔄 REGISTRO MULTI-RECURSO DE MOVIMIENTOS")
    st.markdown("---")
    
    with st.form("form_cabecera"):
        st.markdown("### 📝 Datos de Cabecera")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            tipo_mov = st.selectbox("Tipo de Movimiento Logístico:", ["Ingreso (Guía de Remisión)", "Egreso (Vale de Salida)"])
            almacen_sel = st.selectbox("Seleccione el Almacén de Operación:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
        with col_c2:
            num_doc = st.text_input("Número de Documento (Ej: GR-001-2045 o V-084)")
            fecha_sel = st.date_input("Fecha de Operación", value=datetime.now().date())
            
        st.markdown("### 🦺 Datos del Personal Responsable")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            solicitante = st.text_input("Solicitante / Cuadrilla:")
        with col_p2:
            supervisor = st.text_input("Ing. Supervisor / Residente:")
        with col_p3:
            encargado = st.text_input("Responsable de Almacén:", value=st.session_state.usuario_actual)
            
        observaciones = st.text_area("Observaciones del Frente de Trabajo / Destino:")
        procesar_cabecera = st.form_submit_button("Confirmar Datos de Cabecera")
        
    if "canasta" not in st.session_state:
        st.session_state.canasta = []
        
    st.markdown("---")
    st.markdown("### 📦 Cargar Recursos al Documento Abierto")
    
    df_maestro = st.session_state.maestro_materiales
    col_mat1, col_mat2 = st.columns([2, 1])
    with col_mat1:
        seleccion_combo = st.selectbox("Seleccione Material de Catálogo Saneamiento:", options=df_maestro['Código'] + " - " + df_maestro['Material'])
    with col_mat2:
        cantidad_item = st.number_input("Cantidad del Recurso:", min_value=1, value=1)
        
    if st.button("➕ Añadir Recurso a la Canasta"):
        cod_item = seleccion_combo.split(" - ")[0]
        nom_item = seleccion_combo.split(" - ")[1]
        uni_item = df_maestro[df_maestro['Código'] == cod_item]['Unidad'].values[0]
        
        st.session_state.canasta.append({
            "Código": cod_item, "Material": nom_item, "Cantidad": cantidad_item, "Unidad": uni_item
        })
        st.toast(f"Añadido: {nom_item} x{cantidad_item}")
        
    if st.session_state.canasta:
        st.markdown("#### 📋 Ítems Listados en el Documento Actual")
        df_canasta = pd.DataFrame(st.session_state.canasta)
        st.dataframe(df_canasta, use_container_width=True)
        
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            if st.button("🧼 Vaciar Canasta", use_container_width=True):
                st.session_state.canasta = []
                st.rerun()
        with col_acc2:
            if st.button("🚀 PROCESAR TRANSACCIÓN COMPLETA", type="primary", use_container_width=True):
                if not num_doc or not solicitante or not supervisor:
                    st.error("❌ Por favor, llene los campos obligatorios de la cabecera antes de procesar.")
                else:
                    # Aquí llamamos a la base de datos para impactar Google Sheets de forma síncrona
                    exito, msg = db.registrar_transaccion(
                        tipo_mov, num_doc, almacen_sel, fecha_sel, solicitante, supervisor, encargado, observaciones, st.session_state.canasta
                    )
                    if exito:
                        st.success(msg)
                        st.session_state.canasta = []
                    else:
                        st.error(msg)

# ==========================================
# MÓDULO 4: CONFIGURACIÓN DE ALMACENES
# ==========================================
elif opcion_menu == "⚙️ Configurar Almacenes (1, 6, 8, 10)":
    st.markdown("# ⚙️ PANEL DE CONFIGURACIÓN CORPORATIVA Y CATÁLOGOS")
    st.markdown("---")
    
    st.markdown("### 📝 Registrar Nuevo Material en el Catálogo Técnico")
    with st.form("form_nuevo_material"):
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            nuevo_cod = st.text_input("Código de Inventario (Ej: HID-PO-02):")
        with col_n2:
            nuevo_nom = st.text_input("Descripción Completa del Material:")
        with col_n3:
            nueva_uni = st.selectbox("Unidad de Medida Oficial:", ["Metros", "Unidades", "Varillas", "Global"])
            
        btn_crear_mat = st.form_submit_button("💾 Dar de Alta en Catálogo Maestro")
        
        if btn_crear_mat:
            if nuevo_cod and nuevo_nom:
                nuevo_row = {"Código": nuevo_cod, "Material": nuevo_nom, "Unidad": nueva_uni}
                st.session_state.maestro_materiales = pd.concat([st.session_state.maestro_materiales, pd.DataFrame([nuevo_row])], ignore_index=True)
                st.success(f"✔️ Material {nuevo_nom} dado de alta con éxito.")
            else:
                st.error("❌ Rellene los campos obligatorios del material.")
                
    st.markdown("### 📋 Catálogo Maestro de Materiales de Saneamiento Autorizados")
    st.dataframe(st.session_state.maestro_materiales, use_container_width=True, hide_index=True)
