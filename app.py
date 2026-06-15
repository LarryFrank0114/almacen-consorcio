import streamlit as st
import pandas as pd
import datetime
import database as db

# 1. CONFIGURACIÓN E INICIALIZACIÓN DE LA APLICACIÓN
st.set_page_config(
    page_title="Consorcio San Miguel - Sistema de Almacenes",
    page_icon="🚰",
    layout="wide"
)

# Acoplamos el backend (Carga datos de Google Sheets o Inicializa la sesión)
db.inicializar_db()

# 2. CONTROL DE ACCESO (AUTENTICACIÓN MIGRADA)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = ""
    st.session_state.rol_actual = ""

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 CONTROL DE ACCESO LOGÍSTICO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Megaproyecto Sectorial Saneamiento 'Nueva Rinconada'</p>", unsafe_allow_html=True)
    
    col_login_1, col_login_2, col_login_3 = st.columns([1, 1.5, 1])
    
    with col_login_2:
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            contrasena = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if btn_login:
                # Credenciales actualizadas para la jefatura corporativa
                if usuario == "larry" and contrasena == "admin123":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Larry Frank Rodriguez"
                    st.session_state.rol_actual = "Jefe de Almacenes"
                    st.success("¡Acceso autorizado con éxito!")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
    st.stop()

# 3. INTERFAZ OPERATIVA PRINCIPAL (LOGUEADO)
# Menú Lateral Corporativo
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.usuario_actual}")
    st.markdown(f"**Rol:** {st.session_state.rol_actual}")
    st.markdown("<p style='color: green; font-size: 0.9em;'>● Conectado a Google Sheets</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📌 MENÚ DE OPERACIONES")
    
    opcion_menu = st.radio(
        "Seleccione un módulo:",
        ["📊 Dashboard Gerencial", "📖 Reporte de Stock Actual", "🔄 Registrar Movimiento (Guías/Vales)", "⚙️ Configurar Almacenes (1, 6, 8, 10)"]
    )
    
    st.markdown("---")
    if st.button("🚪 Salir del Sistema", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# 4. DESARROLLO DE LOS MÓDULOS DEL SISTEMA

# ==========================================
# MÓDULO 1: DASHBOARD GERENCIAL
# ==========================================
if opcion_menu == "📊 Dashboard Gerencial":
    st.markdown("# 📊 DASHBOARD CORPORATIVO DE MOVIMIENTOS")
    st.markdown("---")
    
    df_hist = st.session_state.historial_movimientos.copy()
    
    if not df_hist.empty:
        # Métricas principales de control logístico
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Movimientos Registrados", len(df_hist))
        with col_m2:
            ingresos_t = len(df_hist[df_hist['Tipo'] == "Ingreso (Guía de Remisión)"])
            st.metric("Total Ingresos (Guías)", ingresos_t)
        with col_m3:
            egresos_t = len(df_hist[df_hist['Tipo'] == "Egreso (Vale de Salida)"])
            st.metric("Total Egresos (Vales)", egresos_t)
            
        st.markdown("### 📈 Resumen de Movimientos Recientes")
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No se registran movimientos transaccionales en el historial para generar gráficos.")

# ==========================================
# MÓDULO 2: REPORTE DE STOCK ACTUAL & CRUD
# ==========================================
elif opcion_menu == "📖 Reporte de Stock Actual":
    st.markdown("# 📖 REPORTE DE STOCK CONSOLIDADO EN TIEMPO REAL")
    st.markdown("---")
    
    df_inv = st.session_state.inventario.copy()
    
    if not df_inv.empty:
        # Filtros rápidos superiores
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_almacen = st.multiselect("Filtrar por Sede / Almacén:", options=df_inv['Almacén'].unique(), default=df_inv['Almacén'].unique())
        with col_f2:
            buscar_mat = st.text_input("🔍 Buscar material por nombre o código:")
            
        # Aplicamos filtros analíticos
        df_show = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
        if buscar_mat:
            df_show = df_show[df_show['Material'].str.contains(buscar_mat, case=False) | df_show['Código'].str.contains(buscar_mat, case=False)]
            
        # Renderizado de tabla principal de inventario
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # 📥 MOTOR NATIVO DE EXPORTACIÓN (COMPATIBLE CON EXCEL)
        st.markdown("### 📥 Panel de Descargas de Reportes Oficiales")
        csv_data = df_show.to_csv(index=False, sep=';').encode('utf-8-sig')
            
        st.download_button(
            label="🟢 Descargar Reporte de Stock para EXCEL (.csv)",
            data=csv_data,
            file_name=f"Reporte_Stock_Consorcio_San_Miguel.csv",
            mime="text/csv"
        )
        
        # 🔄 ADICIÓN: PANEL CRUD DE MODIFICACIÓN Y ELIMINACIÓN
        st.markdown("---")
        st.markdown("### 🛠️ Panel de Gestión de Recursos (CRUD)")
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            almacen_crud = st.selectbox("1. Seleccione Almacén del recurso a modificar:", options=df_inv['Almacén'].unique(), key="crud_almacen")
        
        materiales_en_almacen = df_inv[df_inv['Almacén'] == almacen_crud]
        
        if not materiales_en_almacen.empty:
            with col_sel2:
                material_crud = st.selectbox("2. Seleccione el Material a modificar:", options=materiales_en_almacen['Código'] + " - " + materiales_en_almacen['Material'], key="crud_material")
            
            codigo_seleccionado = material_crud.split(" - ")[0]
            fila_actual = df_inv[(df_inv['Código'] == codigo_seleccionado) & (df_inv['Almacén'] == almacen_crud)].iloc[0]
            
            with st.form("form_edicion_crud"):
                st.markdown(f"**Modificando:** {fila_actual['Material']} en **{almacen_crud}**")
                col_ed1, col_ed2, col_ed3 = st.columns(3)
                with col_ed1:
                    nuevo_stock = st.number_input("Editar Cantidad (Stock Actual):", value=int(fila_actual['Stock']), min_value=0)
                with col_ed2:
                    nueva_ubica = st.text_input("Editar Ubicación Física:", value=str(fila_actual['Ubicación']))
                with col_ed3:
                    nuevo_encargado = st.text_input("Editar Encargado/Responsable:", value=str(fila_actual['Encargado']))
                    
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    btn_actualizar = st.form_submit_button("💾 Guardar Cambios Actualizados", use_container_width=True)
                with col_btn2:
                    btn_eliminar = st.form_submit_button("❌ Eliminar Recurso del Inventario", use_container_width=True)
                    
                if btn_actualizar:
                    idx_dest = df_inv[(df_inv['Código'] == codigo_seleccionado) & (df_inv['Almacén'] == almacen_crud)].index
                    st.session_state.inventario.at[idx_dest[0], 'Stock'] = nuevo_stock
                    st.session_state.inventario.at[idx_dest[0], 'Ubicación'] = nueva_ubica
                    st.session_state.inventario.at[idx_dest[0], 'Encargado'] = nuevo_encargado
                    db.sincronizar_a_google_sheets(st.session_state.inventario)
                    st.success("✔️ ¡Recurso actualizado en la base de datos!")
                    st.rerun()
                    
                if btn_eliminar:
                    idx_dest = df_inv[(df_inv['Código'] == codigo_seleccionado) & (df_inv['Almacén'] == almacen_crud)].index
                    st.session_state.inventario = df_inv.drop(idx_dest).reset_index(drop=True)
                    db.sincronizar_a_google_sheets(st.session_state.inventario)
                    st.warning("🗑️ El recurso ha sido eliminado de la base de datos.")
                    st.rerun()
        else:
            st.info("No hay materiales registrados en este almacén.")
    else:
        st.info("El inventario se encuentra vacío en la nube de Google Sheets.")

# ==========================================
# MÓDULO 3: REGISTRAR MOVIMIENTOS
# ==========================================
elif opcion_menu == "🔄 Registrar Movimiento (Guías/Vales)":
    st.markdown("# 🔄 REGISTRO MULTI-RECURSO DE INGRESOS Y EGRESOS")
    st.markdown("---")
    
    # Formulario unificado de cabecera con botón de cierre obligatorio
    with st.form("form_cabecera"):
        st.markdown("### 📝 Datos de Cabecera")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            tipo_mov = st.selectbox("Tipo de Movimiento Logístico:", ["Ingreso (Guía de Remisión)", "Egreso (Vale de Salida)"])
            almacen_sel = st.selectbox("Seleccione el Almacén de Operación:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
        with col_c2:
            num_doc = st.text_input("Número de Documento (Ej: GR-001-2045 o V-084)")
            fecha_sel = st.date_input("Fecha de Operación", value=datetime.date.today())
            
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
        
    # Inicializar la canasta de materiales temporal si no existe
    if 'canasta' not in st.session_state:
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
                    st.error("❌ Por favor, rellene todos los campos obligatorios de la cabecera antes de procesar.")
                else:
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
