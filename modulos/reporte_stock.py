import streamlit as st
import pandas as pd
import database as db
import re

def extraer_coordenadas_o_url(texto):
    """Convierte un enlace normal de Google Maps en un mapa embebido integrable en iframe"""
    if "maps.google" in texto or "googlesource" in texto or texto.startswith("http"):
        # Si es un enlace para compartir normal, intentamos formatearlo para embed
        if "embed" not in texto:
            # Reemplazo rápido para forzar la visualización de mapas embebidos interactivos
            return texto.replace("/maps/", "/maps/embed/")
        return texto
    
    # Si ingresaron coordenadas directamente tipo "-12.0463, -77.0427"
    patron = r'[-+]?\d*\.\d+|\d+'
    coordenadas = re.findall(patron, texto)
    if len(coordenadas) >= 2:
        lat, lon = coordenadas[0], coordenadas[1]
        return f"https://maps.google.com/maps?q={lat},{lon}&z=15&output=embed"
    return None

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
        almacenes_permitidos = list(df_inv['Almacén'].unique())

    # Selector de sedes a auditar
    if es_admin_o_super or (not es_admin_o_super and ver_todo):
        filtro_almacen = st.multiselect("Seleccione las sedes a visualizar:", options=list(df_inv['Almacén'].unique()), default=almacenes_permitidos)
    else:
        filtro_almacen = almacenes_permitidos

    buscar = st.text_input("Filtrar recurso por palabra clave (Material o Código):")

    # Filtrar el dataframe
    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar:
        df_filtrado = df_filtrado[df_filtrado['Material'].astype(str).str.contains(buscar, case=False) | df_filtrado['Código'].astype(str).str.contains(buscar, case=False)]

    # Desplegar tabla oficial
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # 🏢 SECCIÓN REDISEÑADA: UBICACIÓN GEOGRÁFICA INTERACTIVA CON MAPAS E IMÁGENES
    st.markdown("---")
    st.markdown("### 🏢 Infraestructura y Ubicación en Tiempo Real")
    
    try:
        df_ubicaciones = pd.DataFrame(sh.worksheet("ubicaciones").get_all_records())
        almacen_a_consultar = filtro_almacen[0] if len(filtro_almacen) == 1 else st.selectbox("Seleccione Almacén para auditar infraestructura:", options=filtro_almacen)
        
        df_ub_sede = df_ubicaciones[df_ubicaciones['Almacen'] == almacen_a_consultar]
        
        if not df_ub_sede.empty:
            info_sede = df_ub_sede.iloc[-1] # Traer el registro más reciente configurado
            
            col_mapa, col_datos = st.columns([1.2, 1])
            
            with col_mapa:
                st.markdown("**📍 Geolocalización Satelital Interactiva**")
                url_mapa = extraer_coordenadas_o_url(str(info_sede['Ubicacion']))
                if url_mapa:
                    # Embeber el mapa de Google Maps directamente en la interfaz de Streamlit
                    st.components.v1.iframe(url_mapa, height=300, scrolling=False)
                else:
                    st.warning("⚠️ El formato del enlace o coordenadas provisto en Ajustes no es válido para incrustar.")
                    st.caption(f"Texto registrado: {info_sede['Ubicacion']}")
            
            with col_datos:
                st.markdown("**📝 Datos de Referencia y Acceso**")
                st.info(f"**Referencias de Ingreso:**\n\n{info_sede['Referencias']}")
                st.caption(f"Configurado por: {info_sede['Configurado_Por']} | Fecha: {info_sede['Fecha']}")
                
                # Visualización de la foto de portada del almacén corregida
                enlace_foto = info_sede['Enlace_Foto']
                if enlace_foto and enlace_foto != "" and not str(enlace_foto).startswith("Error"):
                    st.markdown("**📸 Foto de Fachada Principal**")
                    
                    # Miniatura interactiva con Popover para agrandar sin perder la vista
                    with st.popover("🔎 Ver Miniatura / Agrandar Imagen de Fachada", use_container_width=True):
                        st.image(enlace_foto, caption=f"Fachada registrada para {almacen_a_consultar}", use_container_width=True)
                        st.markdown(f"[🔗 Enlace Directo Alternativo]({enlace_foto})")
                else:
                    st.caption("ℹ️ No se cargó ninguna foto de fachada o el formato de almacenamiento de Drive aún está procesándose.")
        else:
            st.info("ℹ️ Este almacén aún no cuenta con coordenadas ni referencias configuradas en Ajustes.")
    except Exception as e:
        st.info("Aún no se ha inicializado o estructurado datos en la pestaña 'ubicaciones' del archivo maestro.")

    # 📷 REGISTRO VISUAL DIARIO Y GALERÍA COMPLETA DE MINIATURAS
    st.markdown("---")
    st.markdown("### 📷 Galería de Inspecciones Registradas por Sede")
    
    col_f1, col_f2 = st.columns([1, 1.8])
    with col_f1:
        st.markdown("#### Subir Nueva Foto")
        almacen_foto = st.selectbox("Sede a registrar foto:", options=almacen_preferencial, key="sb_foto")
        imagen_cargada = st.file_uploader("Captura (.png, .jpg)", type=["png", "jpg", "jpeg"])
        
        if imagen_cargada is not None:
            st.image(imagen_cargada, caption="Vista Previa Interna", width=200)
            if st.button("Subir e Inmortalizar en Servidor"):
                enlace_drive = db.guardar_foto_drive(imagen_cargada, almacen_foto, user)
                if enlace_drive:
                    st.success(f"Foto vinculada con éxito para {almacen_foto}")
                    st.rerun()

    with col_f2:
        st.markdown("#### Historial Fotográfico (Miniaturas Expandibles)")
        try:
            df_fotos = pd.DataFrame(sh.worksheet("fotos").get_all_records())
            df_fotos_filtradas = df_fotos[df_fotos['Almacen'].isin(filtro_almacen)]
            
            if not df_fotos_filtradas.empty:
                # Mostrar las últimas 6 fotos en un grid limpio de miniaturas de 3 columnas
                registros = df_fotos_filtradas.iloc[::-1].head(6)
                
                # Crear filas dinámicas de 3 columnas para las miniaturas
                for i in range(0, len(registros), 3):
                    cols_grid = st.columns(3)
                    for j, (_, row) in enumerate(registros.iloc[i:i+3].iterrows()):
                        with cols_grid[j]:
                            # Miniatura limpia
                            st.markdown(f"**{row['Almacen']}**")
                            st.caption(f"📅 {row['Fecha']}")
                            
                            # Validar que no sea el link placeholder roto de la plantilla por defecto
                            if "tu_id_de_carpeta" in str(row['Enlace']):
                                st.error("⚠️ Enlace no configurado en Base de Datos.")
                            else:
                                # Contenedor expandible nativo para agrandar con un solo clic
                                with st.popover("🔎 Ver Foto", use_container_width=True):
                                    st.image(row['Enlace'], use_container_width=True, caption=f"Subido por: {row['Usuario']}")
                                    st.markdown(f"[🔗 Enlace de descarga]({row['Enlace']})")
            else:
                st.info("No se registran inspecciones visuales para los almacenes seleccionados.")
        except Exception as e:
            st.info("Aún no hay registros en la base de datos de imágenes o la pestaña 'fotos' está vacía.")
