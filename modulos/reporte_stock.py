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
    
    if "Piero Pezo" in user:
        almacenes_permitidos = ["Almacén 10"]
    elif "Marcial Huayta" in user:
        almacenes_permitidos = ["Almacén 8"]
    elif "Enrique Sanchez" in user:
        almacenes_permitidos = ["Almacén 6"]
    elif "Gregorio Rodriguez" in user:
        almacenes_permitidos = ["Almacén 1"]
    else:
        # Larry y Supervisión tienen acceso total y pueden seleccionar
        almacenes_permitidos = list(df_inv['Almacén'].unique())

    # Selector restringido o informativo según corresponda
    if len(almacenes_permitidos) == 1:
        st.info(f"Visualizando datos asignados exclusivamente a tu cargo: **{almacenes_permitidos[0]}**")
        filtro_almacen = almacenes_permitidos
    else:
        filtro_almacen = st.multiselect("Seleccione las sedes a auditar:", options=almacenes_permitidos, default=almacenes_permitidos)

    buscar = st.text_input("Filtrar recurso por palabra clave:")

    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar:
        df_filtrado = df_filtrado[df_filtrado['Material'].astype(str).str.contains(buscar, case=False)]

    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # 📸 CONTROL VISUAL PERSISTENTE (FOTOS POR ALMACÉN)
    st.markdown("---")
    st.markdown("### 📷 Registro e Historial Fotográfico por Sede")
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.markdown("#### Subir Inspección")
        # El usuario común solo puede subir fotos de su almacén asignado
        almacen_foto = st.selectbox("Sede a registrar foto:", options=almacenes_permitidos, key="sb_foto")
        imagen_cargada = st.file_uploader("Captura (.png, .jpg)", type=["png", "jpg", "jpeg"])
        
        if imagen_cargada is not None:
            st.image(imagen_cargada, caption="Vista Previa", width=250)
            if st.button("Subir e Inmortalizar en Servidor"):
                # Se guarda en Google Drive y se anota el enlace en la hoja "fotos" de Sheets
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
                    # Mostramos el enlace interactivo
                    st.markdown(f"[🔗 Ver Fotografía en Pantalla Completa ({row['Almacen']})]({row['Enlace']})")
                    st.markdown("---")
            else:
                st.info("No se registran inspecciones visuales para los almacenes seleccionados.")
        except:
            st.info("Aún no hay registros en la base de datos de imágenes.")
