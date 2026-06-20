import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh):
    st.markdown("<h2 style='color: #E5A93C;'>📢 Comunicados y Novedades Operativas</h2>", unsafe_allow_html=True)
    
    try:
        ws_anuncios = sh.worksheet("anuncios")
        datos = ws_anuncios.get_all_records()
        df_anuncios = pd.DataFrame(datos)
    except Exception as e:
        st.error(f"Error al cargar anuncios: {e}")
        return

    user_activo = st.session_state.get("username", "Invitado").lower().strip()
    es_admin = user_activo in ["larry", "supervisor", "admin"]

    # ==========================================
    # 🛠️ PANEL DE COMANDANCIA (SOLO ADMINS)
    # ==========================================
    if es_admin:
        with st.expander("🛠️ Panel de Control de Anuncios (Publicar / Editar)"):
            accion = st.radio("Selecciona una acción:", ["Publicar Nuevo", "Modificar Existente"])
            
            if accion == "Publicar Nuevo":
                nuevo_titulo = st.text_input("Título del Anuncio:")
                nuevo_contenido = st.text_area("Contenido del Mensaje:")
                
                if st.button("🚀 Publicar Anuncio", use_container_width=True):
                    if nuevo_titulo and nuevo_contenido:
                        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                        ws_anuncios.append_row([fecha_actual, user_activo, nuevo_titulo, nuevo_contenido])
                        st.success("¡Anuncio publicado con éxito!")
                        st.rerun()
            
            elif accion == "Modificar Existente" and not df_anuncios.empty:
                # Elegir el anuncio por su título
                opciones_anuncios = df_anuncios['Titulo'].tolist()
                anuncio_sel = st.selectbox("Selecciona el anuncio a modificar:", opciones_anuncios)
                
                # Obtener índice y datos actuales
                idx = opciones_anuncios.index(anuncio_sel)
                fila_sheets = idx + 2 # +2 por el encabezado de Sheets
                
                edit_titulo = st.text_input("Editar Título:", value=df_anuncios.iloc[idx]['Titulo'])
                edit_contenido = st.text_area("Editar Contenido:", value=df_anuncios.iloc[idx]['Contenido'])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar Cambios", use_container_width=True):
                        ws_anuncios.update_cell(fila_sheets, 3, edit_titulo) # Columna 3: Titulo
                        ws_anuncios.update_cell(fila_sheets, 4, edit_contenido) # Columna 4: Contenido
                        st.success("¡Anuncio actualizado!")
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ Eliminar Anuncio", use_container_width=True, type="primary"):
                        ws_anuncios.delete_rows(fila_sheets)
                        st.warning("Anuncio eliminado.")
                        st.rerun()

    # ==========================================
    # 👀 VISTA DE LOS ANUNCIOS (CON ALTO CONTRASTE)
    # ==========================================
    if not df_anuncios.empty:
        # Mostrar los anuncios del más reciente al más antiguo
        for _, row in df_anuncios.iloc[::-1].iterrows():
            st.markdown(f"""
                <div style="background-color: #1E1E1E; padding: 20px; border-radius: 12px; border-left: 5px solid #E5A93C; margin-bottom: 15px; border: 1px solid #333333;">
                    <h3 style="margin: 0 0 5px 0; color: #E5A93C !important;">{row['Titulo']}</h3>
                    <p style="margin: 0 0 15px 0; color: #A5A5A5; font-size: 12px;">⏳ {row['Fecha']} — Publicado por: <span style="color:#E5A93C;">{row['Usuario']}</span></p>
                    <p style="color: #FFFFFF !important; font-size: 15px; line-height: 1.5;">{row['Contenido']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay comunicados activos en este momento.")
