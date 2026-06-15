import streamlit as st
import database as db
import auth
import pandas as pd
import io

# Configuración inicial del portal
st.set_page_config(page_title="Consorcio San Miguel - Sistema Logístico", page_icon="🏗️", layout="wide")

db.inicializar_db()
auth.verificar_sesion()

if not st.session_state.logged_in:
    auth.login_form()
else:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown(f"### 🧑‍💻 {st.session_state.username}")
        st.caption(f"Perfil técnico: {st.session_state.user_role}")
        st.markdown("---")
        
        opcion = st.radio(
            "📌 MENÚ DE OPERACIONES",
            [
                "📊 Dashboard Gerencial",
                "📖 Reporte de Stock Actual",
                "🔄 Registrar Movimiento (Guías/Vales)",
                "📍 Configurar Almacenes (1, 6, 8, 10)"
            ]
        )
        st.markdown("---")
        if st.button("🚪 Salir del Sistema"):
            st.session_state.logged_in = False
            st.rerun()

   # --- 1. DASHBOARD PROFESIONAL GERENCIAL ---
    if opcion == "📊 Dashboard Gerencial":
        st.markdown("<h2 style='color:#1E3A8A; font-weight:800;'>📊 DASHBOARD CORPORATIVO DE MOVIMIENTOS</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        df_hist = st.session_state.historial_movimientos.copy()
        
        # Corrección del error: Convertir a fecha y asegurar la creación de columnas de tiempo
        df_hist['Fecha_DT'] = pd.to_datetime(df_hist['Fecha'], errors='coerce')
        df_hist['Mes'] = df_hist['Fecha_DT'].dt.strftime('%Y-%m').fillna(df_hist['Fecha'].str[:7])
        df_hist['Día'] = df_hist['Fecha_DT'].dt.strftime('%Y-%m-%d').fillna(df_hist['Fecha'])
        
        # Filtros de configuración interactiva solicitados
        st.markdown("### 🎛️ Filtros de Análisis Gerencial")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            meses_disp = df_hist['Mes'].unique().tolist()
            filtro_mes = st.multiselect("Filtrar por Mes de Salida:", options=meses_disp, default=meses_disp)
        with col_f2:
            dias_disp = df_hist['Día'].unique().tolist()
            filtro_dia = st.multiselect("Filtrar por Día Específico:", options=dias_disp, default=dias_disp)
        with col_f3:
            sups_disp = df_hist['Supervisor'].unique().tolist()
            filtro_sup = st.multiselect("Filtrar por Supervisor Solicitante:", options=sups_disp, default=sups_disp)
            
        # Aplicación de los filtros al dataframe del Dashboard
        df_dash = df_hist[
            (df_hist['Mes'].isin(filtro_mes)) & 
            (df_hist['Día'].isin(filtro_dia)) & 
            (df_hist['Supervisor'].isin(filtro_sup)) &
            (df_hist['Tipo'] == "Egreso (Vale de Salida)")
        ]
        
        # Indicadores Clave de Rendimiento (KPIs)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Recursos Despachados (Filtrado)", int(df_dash['Cantidad'].sum()) if not df_dash.empty else 0)
        with kpi2:
            st.metric("Transacciones / Vales Atendidos", len(df_dash['Documento'].unique()) if not df_dash.empty else 0)
        with kpi3:
            st.metric("Supervisores Activos en Frentes", len(df_dash['Supervisor'].unique()) if not df_dash.empty else 0)
            
        st.markdown("---")
        
        # Gráficos de barra nativos e intuitivos de Streamlit
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### 📅 Salidas Acumuladas por Día")
            if not df_dash.empty:
                chart_dia = df_dash.groupby('Día')['Cantidad'].sum()
                st.bar_chart(chart_dia)
            else:
                st.caption("No hay datos para los filtros seleccionados.")
                
        with col_g2:
            st.markdown("#### 👨‍💼 Consumo de Materiales por Supervisor Solicitante")
            if not df_dash.empty:
                chart_sup = df_dash.groupby('Supervisor')['Cantidad'].sum()
                st.bar_chart(chart_sup)
            else:
                st.caption("No hay datos para los filtros seleccionados.")

    # --- 2. REPORTE DE STOCK ACTUAL CON EXPORTADOR EXCEL ---
    elif opcion == "📖 Reporte de Stock Actual":
        st.markdown("<h2 style='color:#1E3A8A;'>📖 MAESTRO DE STOCK EN TIEMPO REAL</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Filtros para la visualización y descarga solicitada
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            alm_filtro = st.selectbox("Filtrar visualización por Almacén:", ["Todos", "Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
        with c_p2:
            buscar_mat = st.text_input("🔍 Buscar material específico por nombre o código:")
            
        df_show = st.session_state.inventario.copy()
        if alm_filtro != "Todos":
            df_show = df_show[df_show['Almacén'] == alm_filtro]
        if buscar_mat:
            df_show = df_show[df_show['Material'].str.contains(buscar_mat, case=False) | df_show['Código'].str.contains(buscar_mat, case=False)]
            
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # 🟢 MOTOR DE EXPORTACIÓN EXCEL SOLICITADO
        st.markdown("### 📥 Panel de Descargas de Reportes Oficiales")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_show.to_excel(writer, sheet_name='Stock_Actual', index=False)
            
        st.download_button(
            label="🟢 Descargar Reporte de Stock en Formato EXCEL (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Reporte_Stock_Consorcio_San_Miguel_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )

    # --- 3. REGISTRAR MOVIMIENTOS (TRANSACCIONES MULTI-RECURSO) ---
    elif opcion == "🔄 Registrar Movimiento (Guías/Vales)":
        st.markdown("<h2 style='color:#1E3A8A;'>🔄 REGISTRO DE MOVIMIENTOS LOGÍSTICOS MULTI-RECURSO</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.session_state.user_role != "Administrador":
            st.warning("🔒 Acceso Restringido. Su usuario actual solo cuenta con permisos de consulta y lectura.")
        else:
            tipo_mov = st.selectbox("Tipo de Operación Logística:", ["Ingreso (Guía de Remisión)", "Egreso (Vale de Salida)", "Ingreso (Vale de Devolución)"])
            
            # Encargados automáticos según configuración
            encargados_dict = {"Almacén 1": "Ing. Eduardo T.", "Almacén 6": "Juan Carlos R.", "Almacén 8": "Carlos M.", "Almacén 10": "Luis A."}
            
            with st.form("Datos de Cabecera de la Transacción"):
                st.markdown("### 📝 Datos de Cabecera")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    almacen_sel = st.selectbox("Seleccione el Almacén de Operación:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"])
                    doc_ref = st.text_input("Número de Documento (Ej: GR-001-2045 o V-084)").upper().strip()
                    fecha_sel = st.date_input("Fecha de Operación", value=datetime.now())
                with col_m2:
                    solicitante_sel = st.text_input("Nombre del Solicitante / Cuadrilla")
                    supervisor_sel = st.text_input("Supervisor que Autoriza (Ej: Ing. Marcos Silva)")
                    obs_sel = st.text_area("Observaciones o Destino del Frente de Obra")
                
                encargado_auto = encargados_dict[almacen_sel]
                st.info(f"📋 **Responsable Técnico Custodio:** {encargado_auto}")
                
                st.markdown("---")
                st.markdown("### 📦 Recursos a Transaccionar (Selección Múltiple)")
                
                # Permite al usuario seleccionar varios materiales al mismo tiempo en la lista
                materiales_maestro = st.session_state.maestro_materiales['Material'].tolist()
                materiales_seleccionados = st.multiselect("Seleccione uno o más recursos para procesar en este documento:", options=materiales_maestro)
                
                lista_recursos_final = []
                if materiales_seleccionados:
                    st.write("Especifique las cantidades para cada recurso seleccionado:")
                    for mat_nom in materiales_seleccionados:
                        df_m = st.session_state.maestro_materiales[st.session_state.maestro_materiales['Material'] == mat_nom].iloc[0]
                        cant = st.number_input(f"Cantidad para: {mat_nom} ({df_m['Unidad']})", min_value=1, value=1, step=1, key=df_m['Código'])
                        lista_recursos_final.append({"Código": df_m['Código'], "Material": df_m['Material'], "Cantidad": int(cant), "Unidad": df_m['Unidad']})
                
                btn_procesar_transaccion = st.form_submit_button("🚀 Procesar Transacción Completa en Vivo")
                
                if btn_procesar_transaccion:
                    if not doc_ref or not solicitante_sel or not supervisor_sel or not lista_recursos_final:
                        st.error("❌ Por favor, complete todos los campos obligatorios y seleccione al menos un recurso.")
                    else:
                        exito, msg = db.registrar_transaccion(tipo_mov, doc_ref, almacen_sel, fecha_sel, solicitante_sel, supervisor_sel, encargado_auto, obs_sel, lista_recursos_final)
                        if exito: st.success(msg)
                        else: st.error(msg)

    # --- 4. CONFIGURAR ALMACENES (1, 6, 8, 10) ---
    elif opcion == "📍 Configurar Almacenes (1, 6, 8, 10)":
        st.markdown("<h2 style='color:#1E3A8A;'>📍 RED DE ALMACENES EXTERNOS CONFIGURADOS</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### 🏛️ Directorio de Sedes Logísticas Activas — Consorcio San Miguel")
        tabla_almacenes = pd.DataFrame([
            {"Sede": "Almacén 1", "Ubicación Geográfica": "Área Base Central / Almacén Principal de Tránsito", "Encargado de Almacén": "Ing. Eduardo T.", "Especialidad en Custodia": "Maquinaria, Equipos Críticos e Insumos Generales"},
            {"Sede": "Almacén 6", "Ubicación Geográfica": "San Juan de Miraflores (SJM) - Zona Sur 1", "Encargado de Almacén": "Juan Carlos R.", "Especialidad en Custodia": "Tuberías Pesadas, Conexiones de Saneamiento y PEAD"},
            {"Sede": "Almacén 8", "Ubicación Geográfica": "Villa María del Triunfo (VMT) - Zona Sur 2", "Encargado de Almacén": "Carlos M.", "Especialidad en Custodia": "Válvulas de Compuerta, Accesorios de Presión y Control Hídrico"},
            {"Sede": "Almacén 10", "Ubicación Geográfica": "Villa El Salvador (VES) - Zona Sur 3", "Encargado de Almacén": "Luis A.", "Especialidad en Custodia": "Accesorios Menores, Pernería Especializada e Hidrantes de Poste"}
        ])
        st.table(tabla_almacenes)
        
        # Coordenadas exactas para mapear la red de tus 4 almacenes en Lima Metropolitana
        map_data = pd.DataFrame({
            'lat': [-12.1520, -12.1644, -12.1702, -12.2111],
            'lon': [-76.9750, -76.9622, -76.9385, -76.9344],
            'Sede': ['Almacén 1 (Central)', 'Almacén 6 (SJM)', 'Almacén 8 (VMT)', 'Almacén 10 (VES)']
        })
        st.markdown("### 🗺️ Mapa de Control Geográfico de Activos")
        st.map(map_data)
