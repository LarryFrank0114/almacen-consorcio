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

# Inyección de estilos CSS personalizados para mejorar el aspecto visual general
st.markdown("""
    <style>
        /* Estilo para las tarjetas de KPI personalizadas */
        .kpi-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
            text-align: center;
            border-left: 5px solid #cccccc;
        }
        .kpi-ingreso { border-left: 5px solid #28a745; }
        .kpi-salida { border-left: 5px solid #dc3545; }
        .kpi-total { border-left: 5px solid #007bff; }
        
        .kpi-number {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 0px;
        }
        .kpi-label {
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
""", unsafe_allow_html=True)

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
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🔐 CONTROL DE ACCESO LOGÍSTICO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; font-size: 16px;'>Megaproyecto Sectorial Saneamiento 'Nueva Rinconada'</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='background-color: #F3F4F6; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        with st.form("formulario_login"):
            usuario = st.text_input("👤 Usuario / Código Transaccional")
            contrasena = st.text_input("🔑 Contraseña de Seguridad", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_ingresar = st.form_submit_button("🔓 Validar Credenciales", use_container_width=True)
            
            if btn_ingresar:
                if usuario.lower() == "larry" and contrasena == "admin123":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Larry Frank Rodriguez"
                    st.session_state.rol_actual = "Jefe de Almacenes"
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Verifique mayúsculas o consulte con Sistemas.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# ESTRUCTURA PRINCIPAL (SIDEBAR - MENÚ)
# ==========================================
with st.sidebar:
    st.markdown(f"<h2 style='color: #1E3A8A; margin-bottom: 5px;'>📦 CONCORCIO</h2><p style='color: gray; margin-top:0px;'>San Miguel Saneamiento</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**Usuario:** {st.session_state.usuario_actual}")
    st.markdown(f"**Cargo:** `{st.session_state.rol_actual}`")
    st.markdown("<span style='color:#28a745; font-weight: bold;'>● Servidor en Línea</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🛠️ NAVEGACIÓN")
    opcion_menu = st.radio(
        "Ir al módulo:",
        [
            "📊 Dashboard Gerencial",
            "📖 Reporte de Stock Actual",
            "🔄 Registrar Movimiento (Guías/Vales)",
            "⚙️ Configurar Almacenes (1, 6, 8, 10)"
        ]
    )
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión del Sistema", use_container_width=True, type="secondary"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.session_state.rol_actual = None
        st.rerun()

# ==========================================
# MÓDULO 1: DASHBOARD GERENCIAL (REDiseñado)
# ==========================================
if opcion_menu == "📊 Dashboard Gerencial":
    st.markdown("# 📊 DASHBOARD GERENCIAL DE MOVIMIENTOS")
    st.markdown("📈 Indicadores clave del flujo logístico y transacciones registradas en tiempo real.")
    st.markdown("---")
    
    try:
        ws_historial = sh.worksheet("historial")
        df_historial = pd.DataFrame(ws_historial.get_all_records())
    except Exception:
        df_historial = pd.DataFrame()
        
    if df_historial.empty:
        st.info("ℹ️ No se registran movimientos transaccionales en el historial de Google Sheets para estructurar el panel analítico.")
    else:
        # Filtrado analítico para contar tipos de transacciones
        total_movs = len(df_historial)
        ingresos = len(df_historial[df_historial['Tipo'].astype(str).str.contains('INGRESO|Ingreso', case=False, na=False)])
        salidas = len(df_historial[df_historial['Tipo'].astype(str).str.contains('SALIDA|Egreso|Salida', case=False, na=False)])
        
        # Fila de Tarjetas Visuales Modernas (KPIs con HTML/CSS)
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.markdown(f"""<div class='kpi-card kpi-total'><div class='kpi-number' style='color:#007bff;'>{total_movs}</div><div class='kpi-label'>📋 Total Operaciones</div></div>""", unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f"""<div class='kpi-card kpi-ingreso'><div class='kpi-number' style='color:#28a745;'>📥 {ingresos}</div><div class='kpi-label'>Guías Procesadas (Ingresos)</div></div>""", unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(f"""<div class='kpi-card kpi-salida'><div class='kpi-number' style='color:#dc3545;'>📤 {salidas}</div><div class='kpi-label'>Vales Emitidos (Salidas)</div></div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sección de Gráficos Analíticos Dinámicos
        st.markdown("### 📊 Análisis de Distribución de Recursos")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("**Flujo de Operaciones por Almacén Sede**")
            if 'Almacén' in df_historial.columns:
                conteo_almacen = df_historial['Almacén'].value_index if hasattr(df_historial['Almacén'], 'value_index') else df_historial['Almacén'].value_counts()
                st.bar_chart(conteo_almacen, color="#1E3A8A")
            else:
                st.caption("Faltan datos de sedes en el historial para graficar.")
                
        with col_g2:
            st.markdown("**Evolución Cronológica de Despachos**")
            if 'Fecha' in df_historial.columns:
                df_historial['Fecha_Formato'] = pd.to_datetime(df_historial['Fecha'], errors='coerce')
                conteo_fecha = df_historial['Fecha'].value_counts().sort_index()
                st.line_chart(conteo_fecha, color="#28a745")
            else:
                st.caption("Faltan datos cronológicos en el historial para graficar.")

        st.markdown("---")
        st.markdown("### 📋 Bitácora Transaccional Reciente")
        st.dataframe(df_historial.tail(10), use_container_width=True, hide_index=True)

# ==========================================
# MÓDULO 2: REPORTE DE STOCK ACTUAL (CON SEMÁFORO DE ALERTAS)
# ==========================================
elif opcion_menu == "📖 Reporte de Stock Actual":
    st.markdown("# 📖 REPORTE DE STOCK CONSOLIDADO EN TIEMPO REAL")
    st.markdown("🔍 Monitoreo de existencias de materiales de saneamiento autorizados en frentes de trabajo.")
    st.markdown("---")
    
    try:
        ws_inv = sh.worksheet("inventario")
        datos_inv = ws_inv.get_all_records()
        df_inv = pd.DataFrame(datos_inv)
    except Exception as e:
        st.error(f"Error al leer la pestaña 'inventario': {e}")
        st.stop()
        
    # Filtros superiores estilizados
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_almacen = st.multiselect("🏢 Filtrar por Sede / Almacén:", options=df_inv['Almacén'].unique(), default=df_inv['Almacén'].unique())
    with col_f2:
        buscar_material = st.text_input("🔍 Búsqueda rápida (Escribe descripción o código):")
        
    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar_material:
        df_filtrado = df_filtrado[
            df_filtrado['Material'].str.contains(buscar_material, case=False) | 
            df_filtrado['Código'].astype(str).str.contains(buscar_material, case=False)
        ]
    
    # 🔴🟡🟢 LÓGICA DE ALERTA VISUAL (STOCK CRÍTICO)
    # Se detecta de forma automática materiales con stock menor o igual a 5 unidades
    materiales_criticos = df_filtrado[df_filtrado['Stock'].astype(int) <= 5]
    if not materiales_criticos.empty:
        st.error(f"🚨 **ALERTA DE SEGURIDAD LOGÍSTICA:** Se han detectado **{len(materiales_criticos)}** recursos en estado de **Stock Crítico (≤ 5 unidades)** o Quiebre Físico. Coordine reposiciones de inmediato.")
        with st.expander("⚠️ Ver Lista de Materiales Críticos a Solicitar"):
            st.table(materiales_criticos[['Almacén', 'Código', 'Material', 'Stock']])
            
    st.markdown("### 📋 Inventario General")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    # Descargas oficiales con formato limpio
    st.markdown("<br>", unsafe_allow_html=True)
    csv = df_filtrado.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button("🟢 Descargar Reporte Consolidado para Excel (.csv)", data=csv, file_name="Reporte_Stock_Consorcio.csv", mime="text/csv")

    # PANEL CRUD (Mantenido funcional y corregido con tildes exactas)
    st.markdown("---")
    st.markdown("### 🛠️ PANEL DE CORRECCIÓN LOGÍSTICA IN SITU")
    
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
                    st.success("✔️ Ficha en la nube actualizada con éxito.")
                    st.rerun()
                else:
                    st.error("❌ No se encontró el registro en la nube.")
    else:
        st.info("No se encontraron materiales registrados en la sede seleccionada.")

# ==========================================
# MÓDULO 3: REGISTRAR MOVIMIENTO (FORMULARIO ESTILIZADO)
# ==========================================
elif opcion_menu == "🔄 Registrar Movimiento (Guías/Vales)":
    st.markdown("# 🔄 REGISTRO MULTI-RECURSO DE MOVIMIENTOS")
    st.markdown("📥 Registre el ingreso de materiales vía Guías de Remisión o despachos a cuadrillas mediante Vales de Salida.")
    st.markdown("---")
    
    with st.form("form_cabecera"):
        st.markdown("### 📝 Datos de Documentación Oficial")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            tipo_mov = st.selectbox("Tipo de Movimiento Logístico:", ["Ingreso (Guía de Remisión)", "Egreso (Vale de Salida)"])
            almacen_sel = st.selectbox("Seleccione el Almacén de Operación:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
        with col_c2:
            num_doc = st.text_input("Número de Documento (Ej: GR-001-2045 o V-084)")
            fecha_sel = st.date_input("Fecha de Operación", value=datetime.now().date())
            
        st.markdown("### 🦺 Personal de Custodia y Control")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            solicitante = st.text_input("Solicitante / Cuadrilla Destino:")
        with col_p2:
            supervisor = st.text_input("Ing. Supervisor / Residente Firme:")
        with col_p3:
            encargado = st.text_input("Responsable de Almacén:", value=st.session_state.usuario_actual, disabled=True)
            
        observaciones = st.text_area("Observaciones Generales de la Operación de Frente:")
        procesar_cabecera = st.form_submit_button("🔒 Bloquear y Confirmar Cabecera")
        
    if "canasta" not in st.session_state:
        st.session_state.canasta = []
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📦 Cargar Recursos al Documento Abierto")
    
    df_maestro = st.session_state.maestro_materiales
    col_mat1, col_mat2 = st.columns([3, 1])
    with col_mat1:
        seleccion_combo = st.selectbox("Seleccione Material del Catálogo Oficial Saneamiento:", options=df_maestro['Código'] + " - " + df_maestro['Material'])
    with col_mat2:
        cantidad_item = st.number_input("Cantidad Despachada / Ingresada:", min_value=1, value=1)
        
    if st.button("➕ Añadir Material Destacado a la Canasta", use_container_width=True):
        cod_item = seleccion_combo.split(" - ")[0]
        nom_item = seleccion_combo.split(" - ")[1]
        uni_item = df_maestro[df_maestro['Código'] == cod_item]['Unidad'].values[0]
        
        st.session_state.canasta.append({
            "Código": cod_item, "Material": nom_item, "Cantidad": cantidad_item, "Unidad": uni_item
        })
        st.toast(f"✔️ Agregado correctamente: {nom_item} x{cantidad_item}")
        
    if st.session_state.canasta:
        st.markdown("#### 📋 Materiales Pre-Listados en el Documento")
        df_canasta = pd.DataFrame(st.session_state.canasta)
        st.dataframe(df_canasta, use_container_width=True)
        
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            if st.button("🧼 Limpiar Documento (Vaciar)", use_container_width=True):
                st.session_state.canasta = []
                st.rerun()
        with col_acc2:
            if st.button("🚀 PROCESAR E IMPACTAR OPERACIÓN EN GOOGLE SHEETS", type="primary", use_container_width=True):
                if not num_doc or not solicitante or not supervisor:
                    st.error("❌ Error de Validación: Faltan campos obligatorios en los datos de cabecera.")
                else:
                    # Aquí la app conecta con el backend de Google Sheets para insertar transacciones
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
    st.markdown("🛠️ Altas de nuevos insumos autorizados en la ficha técnica maestro del megaproyecto.")
    st.markdown("---")
    
    st.markdown("### 📝 Registrar Nuevo Material en el Catálogo Técnico")
    with st.form("form_nuevo_material"):
        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            nuevo_cod = st.text_input("Código de Inventario Único (Ej: HID-PO-02):")
        with col_n2:
            nuevo_nom = st.text_input("Descripción Completa y Especificación del Material:")
        with col_n3:
            nueva_uni = st.selectbox("Unidad de Medida Oficial:", ["Metros", "Unidades", "Varillas", "Global"])
            
        btn_crear_mat = st.form_submit_button("💾 Dar de Alta en Catálogo Maestro")
        
        if btn_crear_mat:
            if nuevo_cod and nuevo_nom:
                nuevo_row = {"Código": nuevo_cod, "Material": nuevo_nom, "Unidad": nueva_uni}
                st.session_state.maestro_materiales = pd.concat([st.session_state.maestro_materiales, pd.DataFrame([nuevo_row])], ignore_index=True)
                st.success(f"✔️ Recurso [{nuevo_nom}] dado de alta de forma exitosa en el catálogo interno.")
            else:
                st.error("❌ Campos obligatorios vacíos.")
                
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Catálogo Maestro de Materiales de Saneamiento Autorizados")
    st.dataframe(st.session_state.maestro_materiales, use_container_width=True, hide_index=True)
