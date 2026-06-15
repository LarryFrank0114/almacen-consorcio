import streamlit as st
import pandas as pd
from datetime import datetime
import database as db  # Conexión con nuestro módulo de Google Sheets

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y SESIÓN
# ==========================================
st.set_page_config(
    page_title="Consorcio San Miguel - Gestión de Almacenes",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed" # Escondemos el sidebar para usar el menú premium superior
)

# INYECCIÓN DE CSS MAESTRO CON LA PALETA DE COLORES DE LA EMPRESA (AZUL Y NARANJA)
st.markdown("""
    <style>
        /* Desactivar márgenes excesivos superiores */
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        
        /* Encabezado Corporativo */
        .header-container {
            background: linear-gradient(135deg, #0B2545 0%, #134074 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            border-bottom: 4px solid #F57C00; /* Naranja de seguridad del logo */
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* Tarjetas de Indicadores Corporativos (KPI Cards) */
        .kpi-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid #E0E0E0;
            transition: transform 0.2s;
        }
        .kpi-card:hover { transform: translateY(-3px); }
        .kpi-total { border-top: 4px solid #134074; }
        .kpi-ingreso { border-top: 4px solid #2E7D32; }
        .kpi-salida { border-top: 4px solid #C62828; }
        
        .kpi-number { font-size: 36px; font-weight: 800; margin-bottom: 2px; }
        .kpi-label { font-size: 13px; color: #555555; font-weight: 600; text-transform: uppercase; }
        
        /* Botones Principales con el Naranja de la Empresa */
        div.stButton > button:first-child {
            background-color: #F57C00 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            border-radius: 6px !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #E65100 !important;
            box-shadow: 0 4px 10px rgba(245,124,0,0.3);
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
if "opcion_menu" not in st.session_state:
    st.session_state.opcion_menu = "📊 Dashboard"

# Cargar catálogo maestro si no existe en sesión
if "maestro_materiales" not in st.session_state:
    st.session_state.maestro_materiales = pd.DataFrame([
        {"Código": "HID-PO-01", "Material": "Tubo Polietileno 110mm Pn10", "Unidad": "Metros"},
        {"Código": "ACC-CR-05", "Material": "Cruceta de Hierro Fundido DN 100", "Unidad": "Unidades"},
        {"Código": "VAL-CO-02", "Material": "Válvula de Compuerta C/Brida 4\"", "Unidad": "Unidades"}
    ])

# Conectar a la base de datos de Google Sheets
sh = db.conectar_sheets()
if sh is None:
    st.error("❌ No se pudo establecer la comunicación con el servidor central de Google Sheets.")
    st.stop()

# ==========================================
# PANTALLA DE CONTROL DE ACCESO (LOGIN)
# ==========================================
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0B2545; font-weight:800;'>CONSORCIO SAN MIGUEL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; font-size: 16px; margin-top:-10px;'>Sistema de Control de Inventarios — Obra 'Nueva Rinconada'</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<div style='background-color: white; padding: 35px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border-top: 5px solid #F57C00;'>", unsafe_allow_html=True)
        with st.form("formulario_login"):
            st.markdown("<h4 style='color:#0B2545; margin-top:0px;'>Iniciar Sesión Administrativa</h4>", unsafe_allow_html=True)
            usuario = st.text_input("👤 Usuario Logístico")
            contrasena = st.text_input("🔑 Contraseña", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_ingresar = st.form_submit_button("INGRESAR AL PANEL", use_container_width=True)
            
            if btn_ingresar:
                if usuario.lower() == "larry" and contrasena == "admin123":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Larry Frank Rodriguez"
                    st.session_state.rol_actual = "Jefe de Almacenes"
                    st.rerun()
                else:
                    st.error("❌ Credenciales inválidas.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# CABECERA CORPORATIVA PREMIUM
# ==========================================
st.markdown(f"""
    <div class="header-container">
        <table style="width:100%; border:none; background:none;">
            <tr>
                <td style="text-align:left; border:none; background:none; padding:0;">
                    <h2 style="margin:0; font-weight:800; letter-spacing: 0.5px; color:white;">CONSORCIO SAN MIGUEL</h2>
                    <p style="margin:0; opacity:0.8; font-size:14px;">📦 Gestión Integral de Almacenes Saneamiento</p>
                </td>
                <td style="text-align:right; border:none; background:none; padding:0; vertical-align:middle;">
                    <span style="font-size:14px; font-weight:600; background:rgba(255,255,255,0.15); padding:8px 15px; border-radius:20px;">
                        🦺 {st.session_state.usuario_actual} ({st.session_state.rol_actual})
                    </span>
                </td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# MENÚ DE NAVEGACIÓN TOTALMENTE RESPONSIVO
# ==========================================
# El componente st.segmented_control se adapta automáticamente convirtiéndose en bloques compactos en teléfonos.
opciones_menu = {
    "📊 Dashboard": "📊 Dashboard",
    "📖 Reporte Stock": "📖 Reporte Stock",
    "🔄 Movimientos": "🔄 Movimientos",
    "⚙️ Ajustes": "⚙️ Ajustes"
}

# Renderizamos el menú superior horizontal
opcion_seleccionada = st.segmented_control(
    "Navegación del Sistema",
    options=list(opciones_menu.keys()),
    default="📊 Dashboard",
    label_visibility="collapsed"
)

if opcion_seleccionada:
    st.session_state.opcion_menu = opcion_seleccionada

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MÓDULO 1: DASHBOARD GERENCIAL
# ==========================================
if st.session_state.opcion_menu == "📊 Dashboard":
    try:
        ws_historial = sh.worksheet("historial")
        df_historial = pd.DataFrame(ws_historial.get_all_records())
    except Exception:
        df_historial = pd.DataFrame()
        
    if df_historial.empty:
        st.info("ℹ️ No se registran movimientos transaccionales en el historial.")
    else:
        total_movs = len(df_historial)
        ingresos = len(df_historial[df_historial['Tipo'].astype(str).str.contains('INGRESO|Ingreso', case=False, na=False)])
        salidas = len(df_historial[df_historial['Tipo'].astype(str).str.contains('SALIDA|Egreso|Salida', case=False, na=False)])
        
        # Tarjetas de KPI estilizadas
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.markdown(f"""<div class='kpi-card kpi-total'><div class='kpi-number' style='color:#134074;'>{total_movs}</div><div class='kpi-label'>📋 Total Operaciones</div></div>""", unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f"""<div class='kpi-card kpi-ingreso'><div class='kpi-number' style='color:#2E7D32;'>📥 {ingresos}</div><div class='kpi-label'>Ingresos (Guías)</div></div>""", unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(f"""<div class='kpi-card kpi-salida'><div class='kpi-number' style='color:#C62828;'>📤 {salidas}</div><div class='kpi-label'>Salidas (Vales)</div></div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos responsivos de Streamlit
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("##### **📊 Actividad por Almacén**")
            if 'Almacén' in df_historial.columns:
                st.bar_chart(df_historial['Almacén'].value_counts(), color="#134074")
        with col_g2:
            st.markdown("##### **📈 Frecuencia Cronológica**")
            if 'Fecha' in df_historial.columns:
                st.line_chart(df_historial['Fecha'].value_counts().sort_index(), color="#F57C00")

# ==========================================
# MÓDULO 2: REPORTE DE STOCK ACTUAL (CON ALERTAS)
# ==========================================
elif st.session_state.opcion_menu == "📖 Reporte Stock":
    try:
        ws_inv = sh.worksheet("inventario")
        df_inv = pd.DataFrame(ws_inv.get_all_records())
    except Exception as e:
        st.error(f"Error al leer la pestaña 'inventario': {e}")
        st.stop()
        
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        filtro_almacen = st.multiselect("🏢 Seleccionar Sedes:", options=df_inv['Almacén'].unique(), default=df_inv['Almacén'].unique())
    with col_f2:
        buscar_material = st.text_input("🔍 Filtrar recurso por nombre o código:")
        
    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar_material:
        df_filtrado = df_filtrado[
            df_filtrado['Material'].str.contains(buscar_material, case=False) | 
            df_filtrado['Código'].astype(str).str.contains(buscar_material, case=False)
        ]
    
    # Alerta de Stock Crítico
    materiales_criticos = df_filtrado[df_filtrado['Stock'].astype(int) <= 5]
    if not materiales_criticos.empty:
        st.error(f"🚨 **Stock Crítico Detectado (≤ 5 unidades):** Existen {len(materiales_criticos)} artículos en riesgo de quiebre. Revise la lista expandible.")
        with st.expander("⚠️ Ver Lista Critica"):
            st.table(materiales_criticos[['Almacén', 'Código', 'Material', 'Stock']])
            
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    # Descarga directa compatible
    csv = df_filtrado.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button("🟢 DESCARGAR REPORTE EXCEL", data=csv, file_name="Stock_Consorcio.csv", mime="text/csv")

    # PANEL CRUD DE EDICIÓN RÁPIDA
    st.markdown("---")
    st.markdown("### 🛠️ PANEL DE CORRECCIÓN LOGÍSTICA IN SITU")
    almacen_crud_sel = st.selectbox("1. Seleccione Almacén a modificar:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
    materiales_en_almacen = df_inv[df_inv['Almacén'].astype(str) == almacen_crud_sel]
    
    if not materiales_en_almacen.empty:
        opciones_combo = materiales_en_almacen['Código'].astype(str) + " - " + materiales_en_almacen['Material'].astype(str)
        material_crud = st.selectbox("2. Seleccione el Material a modificar:", options=opciones_combo)
        
        codigo_seleccionado = material_crud.split(" - ")[0]
        datos_material = materiales_en_almacen[materiales_en_almacen['Código'].astype(str) == codigo_seleccionado].iloc[0]
        
        with st.form("form_edicion_rapida"):
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                nuevo_stock = st.number_input("Stock Real:", value=int(datos_material['Stock']), min_value=0)
            with col_e2:
                nueva_ubica = st.text_input("Ubicación Interna:", value=str(datos_material['Ubicación']))
            with col_e3:
                nuevo_encargado = st.text_input("Custodio:", value=str(datos_material['Encargado']))
                
            if st.form_submit_button("💾 GUARDAR CAMBIOS EN LA NUBE"):
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
                    st.success("✔️ Ficha actualizada.")
                    st.rerun()
    else:
        st.info("Sin registros en esta sede.")

# ==========================================
# MÓDULO 3: REGISTRAR MOVIMIENTO
# ==========================================
elif st.session_state.opcion_menu == "🔄 Movimientos":
    st.markdown("### 🔄 REGISTRO MULTI-RECURSO DE MOVIMIENTOS")
    
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
        st.form_submit_button("🔒 Confirmar Cabecera")
        
    if "canasta" not in st.session_state:
        st.session_state.canasta = []
        
    st.markdown("---")
    st.markdown("##### **📦 Agregar Insumos al Documento Abierto**")
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
        st.toast(f"✔️ Agregado: {nom_item}")
        
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
                    st.error("❌ Faltan datos en la cabecera.")
                else:
                    exito, msg = db.registrar_transaccion(
                        tipo_mov, num_doc, almacen_sel, fecha_sel, solicitante, supervisor, st.session_state.usuario_actual, observaciones, st.session_state.canasta
                    )
                    if exito:
                        st.success(msg)
                        st.session_state.canasta = []
                    else:
                        st.error(msg)

# ==========================================
# MÓDULO 4: CONFIGURACIÓN DE ALMACENES
# ==========================================
elif st.session_state.opcion_menu == "⚙️ Ajustes":
    st.markdown("### ⚙️ PANEL DE CONFIGURACIÓN Y CATÁLOGOS TÉCNICOS")
    
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
                st.success("✔️ Insumo agregado.")
            else:
                st.error("❌ Complete los campos.")
                
    st.dataframe(st.session_state.maestro_materiales, use_container_width=True, hide_index=True)

# ==========================================
# BOTÓN DE CIERRE DE SESIÓN EN PARTE INFERIOR PARA MÓVILES
# ==========================================
st.markdown("<br><hr>", unsafe_allow_html=True)
if st.button("🚪 Salir de Cuenta", key="btn_salir_movil"):
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.session_state.rol_actual = None
    st.rerun()
