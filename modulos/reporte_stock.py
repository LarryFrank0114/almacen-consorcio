import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

def render(sh):
    st.markdown("### Reporte de Existencias Consolidadas")
    st.markdown("---")
    
    try:
        ws_inv = sh.worksheet("inventario")
        df_inv = pd.DataFrame(ws_inv.get_all_records())
    except Exception as e:
        st.error(f"Error de lectura en inventarios: {e}")
        return

    # 🔐 REGLA DE NEGOCIO: FILTRADO ESTRICTO SEGÚN IDENTIDAD DEL USUARIO
    user = st.session_state.username
    
    # Determinar almacén preferencial o técnico asignado
    if "Piero Pezo" in user:
        almacen_preferencial = ["Almacén 10"]
    elif "Marcial Huayta" in user:
        almacen_preferencial = ["Almacén 8"]
    elif "Enrique Sanchez" in user:
        almacen_preferencial = ["Almacén 6"]
    elif "Gregorio Rodriguez" in user:
        almacen_preferencial = ["Almacén 1"]
    else:
        almacen_preferencial = list(df_inv['Almacén'].unique())

    # Switch visual para permitir ver el stock global (Modo Consulta)
    es_admin_o_super = "Larry" in user or "Supervisor" in user
    
    if not es_admin_o_super:
        st.info(f"📍 Tu sede preferencial asignada: **{almacen_preferencial[0]}**")
        ver_todo = st.checkbox("🔍 Deseo consultar el Stock Actual de otros almacenes (Solo Lectura)")
        if ver_todo:
            almacenes_permitidos = list(df_inv['Almacén'].unique())
        else:
            almacenes_permitidos = almacen_preferencial
    else:
        # Larry y Supervisión tienen acceso total inmediato
        almacenes_permitidos = list(df_inv['Almacén'].unique())

    # Selector de sedes a auditar (se muestra si tiene acceso total o activó el switch)
    if es_admin_o_super or (not es_admin_o_super and ver_todo):
        filtro_almacen = st.multiselect("Seleccione las sedes a visualizar:", options=list(df_inv['Almacén'].unique()), default=almacenes_permitidos)
    else:
        filtro_almacen = almacenes_permitidos

    buscar = st.text_input("Filtrar recurso por palabra clave (Material o Código):")

    # Filtrar el dataframe
    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar:
        df_filtrado = df_filtrado[df_filtrado['Material'].astype(str).str.contains(buscar, case=False) | df_filtrado['Código'].astype(str).str.contains(buscar, case=False)]

    # Desplegar tabla oficial sin índices en modo lectura
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # 📸 MOSTRAR INFORMACIÓN GEOGRÁFICA Y DE REFERENCIAS DEL ALMACÉN SELECCIONADO
    st.markdown("---")
    st.markdown("### 🏢 Ubicación y Datos de Referencia de Sedes")
    try:
        df_ubicaciones = pd.DataFrame(sh.worksheet("ubicaciones").get_all_records())
        # Si se está filtrando un único almacén en la tabla superior o seleccionado en el combo, mostrar sus datos
        almacen_a_consultar = filtro_almacen[0] if len(filtro_almacen) == 1 else st.selectbox("Seleccione Almacén para ver detalles de infraestructura:", options=filtro_almacen)
        
        df_ub_sede = df_ubicaciones[df_ubicaciones['Almacen'] == almacen_a_consultar]
        if not df_ub_sede.empty:
            info_sede = df_ub_sede.iloc[-1] # Traer el registro más reciente configurado
            col_inf1, col_inf2 = st.columns([1, 1])
            with col_inf1:
                st.markdown(f"**📍 Coordenadas / Enlace de Ubicación:**")
                st.write(info_sede['Ubicacion'])
                st.markdown(f"**📝 Referencias de Acceso:**")
                st.info(info_sede['Referencias'])
            with col_inf2:
                if info_sede['Enlace_Foto'] and info_sede['Enlace_Foto'] != "":
                    st.markdown("**📸 Fotografía de Fachada / Lugar:**")
                    st.markdown(f"[🔗 Abrir Imagen en Alta Resolución]({info_sede['Enlace_Foto']})")
        else:
            st.info("ℹ️ Este almacén aún no cuenta con coordenadas ni referencias configuradas en Ajustes.")
    except Exception as e:
        st.info("Aún no se ha inicializado la pestaña de 'ubicaciones' en el Google Sheet central.")

    # 📸 CONTROL VISUAL PERSISTENTE (HISTORIAL DE INSPECCIONES)
    st.markdown("---")
    st.markdown("### 📷 Historial de Fotos de Inspección por Sede")
    
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        st.markdown("#### Subir Nueva Inspección Diaria")
        almacen_foto = st.selectbox("Sede a registrar foto:", options=almacen_preferencial, key="sb_foto")
        imagen_cargada = st.file_uploader("Captura (.png, .jpg)", type=["png", "jpg", "jpeg"])
        
        if imagen_cargada is not None:
            st.image(imagen_cargada, caption="Vista Previa", width=250)
            if st.button("Subir e Inmortalizar en Servidor"):
                enlace_drive = db.guardar_foto_drive(imagen_cargada, almacen_foto, user)
                if enlace_drive:
                    st.success(f"Foto enlazada con éxito para {almacen_foto}")
                    st.rerun()

    with col_f2:
        st.markdown("#### Galería de Inspecciones Registradas")
        try:
            df_fotos = pd.DataFrame(sh.worksheet("fotos").get_all_records())
            df_fotos_filtradas = df_fotos[df_fotos['Almacen'].isin(filtro_almacen)]
            
            if not df_fotos_filtradas.empty:
                for _, row in df_fotos_filtradas.iloc[::-1].head(4).iterrows():
                    st.markdown(f"**Sede:** {row['Almacen']} | **Fecha:** {row['Fecha']} | **Subido por:** {row['Usuario']}")
                    st.markdown(f"[🔗 Ver Fotografía en Pantalla Completa]({row['Enlace']})")
                    st.markdown("---")
            else:
                st.info("No se registran inspecciones visuales para los almacenes seleccionados.")
        except:
            st.info("Aún no hay registros en la base de datos de imágenes.")
