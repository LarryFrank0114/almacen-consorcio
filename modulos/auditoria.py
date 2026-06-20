import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

def render(sh):
    st.markdown("### 📋 Auditoría y Conteo Físico de Terreno")
    st.markdown("---")
    
    user = st.session_state.username
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M")

    # 1. Cargar datos del inventario para conocer el stock teórico actual
    try:
        ws_inv = sh.worksheet("inventario")
        df_inv = pd.DataFrame(ws_inv.get_all_records())
    except Exception as e:
        st.error(f"Error al conectar con la pestaña de inventarios: {e}")
        return

    # Determinar almacén por defecto según perfil de usuario
    if "Piero Pezo" in user:
        almacen_defecto = "Almacén 10"
    elif "Marcial Huayta" in user:
        almacen_defecto = "Almacén 8"
    elif "Enrique Sanchez" in user:
        almacen_defecto = "Almacén 6"
    elif "Gregorio Rodriguez" in user:
        almacen_defecto = "Almacén 1"
    else:
        almacen_defecto = "Almacén 1"

    # Componentes del Formulario en Layout Limpio
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("##### 📍 Parámetros del Auditor")
        st.disabled_input = st.text_input("Auditor Activo:", value=user, disabled=True)
        
        # Filtro de Almacenes disponibles en el maestro
        lista_almacenes = list(df_inv['Almacén'].unique()) if not df_inv.empty else [almacen_defecto]
        if almacen_defecto not in lista_almacenes:
            lista_almacenes.append(almacen_defecto)
            
        almacen_sel = st.selectbox("Almacén a Auditar:", options=lista_almacenes, index=lista_almacenes.index(almacen_defecto))

    with col2:
        st.markdown("##### 📅 Registro Cronológico")
        st.text_input("Fecha de Control:", value=fecha_hoy, disabled=True)
        st.text_input("Hora de Captura:", value=hora_actual, disabled=True)

    st.markdown("---")
    st.markdown("##### 📦 Conteo de Materiales Críticos")

    # Filtrar materiales que pertenecen únicamente al almacén seleccionado
    if not df_inv.empty:
        df_local = df_inv[df_inv['Almacén'] == almacen_sel]
        lista_materiales = df_local['Material'].unique().tolist()
    else:
        lista_materiales = []

    if not lista_materiales:
        st.warning("⚠️ No se registran stocks previos en este almacén. Selecciona un ítem de control general.")
        try:
            ws_maestro = sh.worksheet("maestro")
            lista_materiales = pd.DataFrame(ws_maestro.get_all_records())['Descripción'].tolist()
        except:
            lista_materiales = ["Varilla Corrugada 1/2''", "Cemento Sol HE", "Tubo PVC 2''"]

    material_sel = st.selectbox("Seleccione el Recurso a Fiscalizar:", options=lista_materiales)

    # Buscar Stock Teórico en Sheets
    stock_teorico = 0
    if not df_inv.empty:
        match = df_inv[(df_inv['Almacén'] == almacen_sel) & (df_inv['Material'] == material_sel)]
        if not match.empty:
            stock_teorico = int(match.iloc[0]['Stock'])

    # Ingreso del conteo físico en campo
    col_conteo, col_preview = st.columns([1, 1.2])
    
    with col_conteo:
        conteo_fisico = st.number_input("Cantidad Física Contada (Unidades/Medida):", min_value=0, value=int(stock_teorico), step=1)
        observaciones = st.text_area("Observaciones o Novedades de la Sede:", placeholder="Ej. Material ordenado en Zona A. Sin signos de corrosión.")
        
        # Cálculo de discrepancias en tiempo real
        discrepancia = conteo_fisico - stock_teorico
        
        if discrepancia == 0:
            st.success(f"⚖️ **Conciliación Perfecta:** El conteo coincide con el Stock Teórico ({stock_teorico} und).")
        else:
            porcentaje_error = (abs(discrepancia) / stock_teorico * 100) if stock_teorico > 0 else 100
            if porcentaje_error > 5:
                st.error(f"🚨 **Alerta de Discrepancia Crítica:** Desfase de {discrepancia} unidades ({porcentaje_error:.1f}% de desviación sobre el sistema).")
            else:
                st.warning(f"⚠️ **Discrepancia Leve:** Desfase de {discrepancia} unidades.")

    with col_preview:
        foto_conteo = st.file_uploader("📸 Evidencia Visual Obligatoria (Foto del Conteo):", type=["jpg", "png", "jpeg"])
        if foto_conteo:
            st.image(foto_conteo, caption="Muestra de Conteo Cargada", width=260)

    st.markdown("---")
    
    # Botón de Procesamiento final de Auditoría
    if st.button("🚀 Enviar Reporte de Auditoría Pro", use_container_width=True, type="primary"):
        if not foto_conteo:
            st.error("❌ Error: Es obligatorio cargar una captura fotográfica como evidencia del conteo físico.")
            return
        
        with st.spinner("Procesando datos y comprimiendo evidencia digital..."):
            # Enviar los datos a la base central de datos
            exito, msg = db.registrar_auditoria_terreno(
                sh, fecha_hoy, hora_actual, user, almacen_sel, material_sel, stock_teorico, conteo_fisico, discrepancia, foto_conteo, observaciones
            )
            
            if exito:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # 📊 Historial de Auditorías Recientes en la parte inferior
    st.markdown("---")
    st.markdown("#### ⏳ Historial de Fiscalizaciones Recientes")
    try:
        ws_aud = sh.worksheet("auditorias")
        df_aud = pd.DataFrame(ws_aud.get_all_records())
        if not df_aud.empty:
            # Mostrar las últimas 10 auditorías en orden descendente
            df_aud_filtrada = df_aud[df_aud['Almacen'] == almacen_sel] if almacen_sel else df_aud
            st.dataframe(df_aud_filtrada.iloc[::-1].head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No se registran auditorías previas indexadas en la nube.")
    except Exception:
        st.info("La pestaña de auditorías está lista para recibir su primer registro técnico.")
