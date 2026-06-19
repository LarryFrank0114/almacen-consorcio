import streamlit as st
import pandas as pd
import database as db
import re

def extraer_coordenadas_o_url(texto):
    """
    Formatea de manera estricta y segura cualquier entrada de Google Maps 
    para forzar que el iFrame de Streamlit cargue el mapa interactivo de forma legal.
    """
    texto_str = str(texto).strip()
    
    # CASO 1: Si es un enlace largo o corto de compartir de Google Maps
    if "maps.google" in texto_str or "goo.gl/maps" in texto_str or texto_str.startswith("http"):
        if "/embed" in texto_str:
            return texto_str
        
        # Intentamos extraer latitud y longitud incrustados en la misma URL de Google Maps (ej: @-12.0431,-77.0254)
        patron_url = r'@([-+]?\d*\.\d+),([-+]?\d*\.\d+)'
        match = re.search(patron_url, texto_str)
        if match:
            lat, lon = match.group(1), match.group(2)
            return f"https://maps.google.com/maps?q={lat},{lon}&z=15&output=embed"
            
        if "q=" not in texto_str:
            return f"https://maps.google.com/maps?q={texto_str}&z=15&output=embed"
        
        return texto_str + "&output=embed"
    
    # CASO 2: Si el usuario ingresó coordenadas puras separadas por coma (ej: -12.0463, -77.0427)
    patron_coor = r'[-+]?\d*\.\d+|\d+'
    coordenadas = re.findall(patron_coor, texto_str)
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

    user = st.session_state.username
    
    # Determinar almacén preferencial por personal
    if "Piero Pezo" in user:
        almacen_preferencial = ["Almacén 10"]
    elif "Marcial Huayta" in user:
        almacen_preferencial = ["Almacén 8"]
    elif "Enrique Sanchez" in user:
        almacen_preferencial = ["Almacén 6"]
    elif "Gregorio Rodriguez" in user:
        almacen_preferencial = ["Almacén 1"]
    else:
        almacen_preferencial = list(df_inv['Almacén'].unique()) if not df_inv.empty else ["Almacén 1"]

    es_admin_o_super = "Larry" in user or "Supervisor" in user
    
    if not es_admin_o_super:
        st.info(f"📍 Sede operativa predeterminada: **{almacen_preferencial[0]}**")
        ver_todo = st.checkbox("🔍 Consultar el Stock de otros almacenes (Modo de Solo Lectura)")
        if ver_todo:
            almacenes_permitidos = list(df_inv['Almacén'].unique()) if not df_inv.empty else almacen_preferencial
        else:
            almacenes_permitidos = almacen_preferencial
    else:
        almacenes_permitidos = list(df_inv['Almacén'].unique()) if not df_inv.empty else ["Almacén 1"]

    if es_admin_o_super or (not es_admin_o_super and ver_todo):
        filtro_almacen = st.multiselect("Seleccione las sedes a visualizar:", options=list(df_inv['Almacén'].unique()) if not df_inv.empty else almacenes_permitidos, default=almacenes_permitidos)
    else:
        filtro_almacen = almacenes_permitidos

    buscar = st.text_input("Filtrar recurso por palabra clave (Material o Código):")

    if not df_inv.empty:
        df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
        if buscar:
            df_filtrado = df_filtrado[df_filtrado['Material'].astype(str).str.contains(buscar, case=False) | df_filtrado['Código'].astype(str).str.contains(buscar, case=False)]
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.info("No hay inventario registrado en este momento.")

    # 🏢 MAPA Y DETALLES DE UBICACIÓN
    st.markdown("---")
    st.markdown("### 🏢 Infraestructura y Croquis de Ubicación")
    
    try:
        df_ubicaciones = pd.DataFrame(sh.worksheet("ubicaciones").get_all_records())
        almacen_a_consultar = filtro_almacen[0] if len(filtro_almacen) == 1 else st.selectbox("Seleccione Almacén para ver referencias de acceso:", options=filtro_almacen)
        
        df_ub_sede = df_ubicaciones[df_ubicaciones['Almacen'] == almacen_a_consultar]
        
        if not df_ub_sede.empty:
            info_sede = df_ub_sede.iloc[-1]
            col_mapa, col_datos = st.columns([1.4, 1])
            
            # Extraer coordenadas limpias para el botón de navegación GPS externa
            raw_ubicacion = str(info_sede['Ubicacion']).strip()
            
            with col_mapa:
                url_mapa = extraer_coordenadas_o_url(raw_ubicacion)
                if url_mapa:
                    st.components.v1.iframe(url_mapa, height=320, scrolling=True)
                else:
                    st.warning("⚠️ Formato de localización vacío o no compatible.")
            
            with col_datos:
                st.markdown("**📝 Datos Técnicos de Entrada**")
                st.info(f"**Referencias:**\n\n{info_sede['Referencias']}")
                
                # 🌐 BOTÓN DE NAVEGACIÓN GPS EN DIRECTO PARA EL SUPERVISOR
                if "," in raw_ubicacion or raw_ubicacion.startswith("http"):
                    link_navegacion = raw_ubicacion if raw_ubicacion.startswith("http") else f"https://www.google.com/maps/search/?api=1&query={raw_ubicacion}"
                    st.link_button("🚗 Iniciar Navegación GPS (Google Maps)", link_navegacion, use_container_width=True, type="primary")
                
                enlace_foto = info_sede['Enlace_Foto']
                if enlace_foto and str(enlace_foto).startswith("data:image"):
                    with st.popover("📸 Ver Foto de Fachada", use_container_width=True):
                        st.image(enlace_foto, caption=f"Fachada de {almacen_a_consultar}", use_container_width=True)
        else:
            st.info("ℹ️ Almacén seleccionado sin parámetros geográficos configurados en Ajustes.")
    except Exception as e:
        st.info(f"Aún no existen registros cartográficos estructurados: {e}")

    # 📷 GALERÍA DE INSPECCIONES EN MINIATURAS
    st.markdown("---")
    st.markdown("### 📷 Galería Fotográfica de Inspección")
    
    col_f1, col_f2 = st.columns([1, 1.8])
    with col_f1:
        st.markdown("#### Subir Registro Visual Diario")
        almacen_foto = st.selectbox("Sede vinculada:", options=almacen_preferencial, key="sb_foto")
        imagen_cargada = st.file_uploader("Capturar archivo (.png, .jpg)", type=["png", "jpg", "jpeg"])
        
        if imagen_cargada is not None:
            st.image(imagen_cargada, caption="Vista Previa", width=180)
            if st.button("Guardar en Historial", use_container_width=True):
                enlace_drive = db.guardar_foto_drive(imagen_cargada, almacen_foto, user)
                if enlace_drive:
                    st.success("Imagen indexada de forma permanente.")
                    st.rerun()

with col_f2:
        st.markdown("#### Mosaico de Capturas Recientes")
        try:
            df_fotos = pd.DataFrame(sh.worksheet("fotos").get_all_records())
            df_fotos_filtradas = df_fotos[df_fotos['Almacen'].isin(filtro_almacen)]
            
            if not df_fotos_filtradas.empty:
                registros = df_fotos_filtradas.iloc[::-1].head(6)
                
                for i in range(0, len(registros), 3):
                    cols_grid = st.columns(3)
                    for k, (_, row) in enumerate(registros.iloc[i:i+3].iterrows()):
                        with cols_grid[k]:
                            st.caption(f"**{row['Almacen']}**\n\n📅 {row['Fecha']}")
                            link_imagen = str(row['Enlace']).strip()
                            
                            # Si hay links en base64 antiguos o links directos de Google Drive configurados
                            if link_imagen.startswith("data:image") or link_imagen.startswith("http"):
                                with st.popover("🔎 Ver Foto", use_container_width=True):
                                    st.image(link_imagen, use_container_width=True, caption=f"Por: {row['Usuario']}")
                            else:
                                st.caption("⚠️ Registro sin origen visual compatible.")
            else:
                st.info("Sin registros fotográficos recientes para estas sedes.")
        except Exception:
            st.info("Sin historial fotográfico disponible.")
