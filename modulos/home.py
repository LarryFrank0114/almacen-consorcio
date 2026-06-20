import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh):
    st.markdown("<h2 style='color: #E5A93C; text-align: center;'>📢 Comunicados y Novedades Operativas</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A5A5A5;'>Consorcio San Miguel — Gestión de Materiales e Infraestructura Externa.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Intentar conectar con la pestaña "anuncios" en Google Sheets
    try:
        ws_anuncios = sh.worksheet("anuncios")
        datos = ws_anuncios.get_all_records()
        df_anuncios = pd.DataFrame(datos)
    except Exception as e:
        st.error(f"⚠️ No se pudo acceder a la pestaña 'anuncios' en Google Sheets: {e}")
        st.info("Asegúrate de tener una pestaña llamada exactamente 'anuncios' con las columnas: Fecha, Usuario, Titulo, Contenido")
        return

    # Verificar si el usuario activo es administrador
    user_activo = st.session_state.get("username", "Invitado").lower().strip()
    es_admin = user_activo in ["larry", "supervisor", "admin", "piero pezo"]

    # =======================================================================
    # 🛠️ PANEL DE GESTIÓN DE ANUNCIOS (EXCLUSIVO PARA LARRY / ADMINS)
    # =======================================================================
    if es_admin:
        with st.expander("⚙️ Panel de Administración de Comunicados (Publicar / Modificar)"):
            accion = st.radio("Elige una acción para el registro:", ["✨ Publicar Nuevo Anuncio", "✏️ Modificar / Eliminar Existente"], horizontal=True)
            
            if accion == "✨ Publicar Nuevo Anuncio":
                nuevo_titulo = st.text_input("Título del Comunicado:", placeholder="Ej: Nueva Directiva de Entrega de EPP")
                nuevo_contenido = st.text_area("Cuerpo del Mensaje / Instrucciones:", placeholder="Escribe los detalles aquí...")
                
                if st.button("🚀 Lanzar Anuncio Oficial", use_container_width=True):
                    if nuevo_titulo and nuevo_contenido:
                        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                        ws_anuncios.append_row([fecha_actual, user_activo, nuevo_titulo, nuevo_contenido])
                        st.success("¡Anuncio publicado correctamente en la base del sistema!")
                        st.rerun()
                    else:
                        st.error("Por favor rellena tanto el título como el contenido.")
            
            elif accion == "✏️ Modificar / Eliminar Existente":
                if not df_anuncios.empty:
                    opciones_anuncios = df_anuncios['Titulo'].tolist()
                    anuncio_sel = st.selectbox("Selecciona el anuncio que deseas gestionar:", opciones_anuncios)
                    
                    # Encontrar el índice de la fila en Sheets
                    idx = opciones_anuncios.index(anuncio_sel)
                    fila_sheets = idx + 2  # +2 debido al encabezado indexado
                    
                    edit_titulo = st.text_input("Editar Título del Comunicado:", value=df_anuncios.iloc[idx]['Titulo'])
                    edit_contenido = st.text_area("Editar Cuerpo del Mensaje:", value=df_anuncios.iloc[idx]['Contenido'])
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("💾 Actualizar y Guardar Cambios", use_container_width=True):
                            ws_anuncios.update_cell(fila_sheets, 3, edit_titulo)      # Columna 3 = Titulo
                            ws_anuncios.update_cell(fila_sheets, 4, edit_contenido)   # Columna 4 = Contenido
                            st.success("¡Comunicado actualizado de forma inmediata!")
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Eliminar Anuncio del Sistema", use_container_width=True, type="primary"):
                            ws_anuncios.delete_rows(fila_sheets)
                            st.warning("El anuncio ha sido removido del historial de campo.")
                            st.rerun()
                else:
                    st.info("No hay anuncios disponibles para modificar.")

    st.markdown("<br>", unsafe_allow_html=True)

    # =======================================================================
    # 👀 SECCIÓN DE VISTA PÚBLICA (CON TARJETAS DE ALTO CONTRASTE)
    # =======================================================================
    if not df_anuncios.empty:
        # Invertimos el DataFrame para que el comunicado más reciente aparezca primero en la pantalla
        for _, row in df_anuncios.iloc[::-1].iterrows():
            st.markdown(f"""
                <div style="background-color: #1F2327; padding: 22px; border-radius: 12px; border-left: 6px solid #E5A93C; margin-bottom: 18px; border-top: 1px solid #343A40; border-right: 1px solid #343A40; border-bottom: 1px solid #343A40; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                    <h3 style="margin: 0 0 6px 0; color: #E5A93C !important; font-size: 19px; font-weight:700;">{row['Titulo']}</h3>
                    <p style="margin: 0 0 14px 0; color: #A5A5A5 !important; font-size: 12px; font-weight:500;">
                        ⏳ Registro: {row['Fecha']} &nbsp;|&nbsp; 👷 Responsable: <span style="color:#E5A93C; font-weight:bold;">{row['Usuario']}</span>
                    </p>
                    <div style="color: #FFFFFF !important; font-size: 14.5px; line-height: 1.6; white-space: pre-wrap; font-family: sans-serif;">{row['Contenido']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background-color: #1F2327; padding: 20px; border-radius: 10px; text-align: center; border: 1px dashed #495057;">
                <p style="color: #A5A5A5 !important; margin: 0;">ℹ️ No existen comunicados vigentes o publicados en la bitácora actual.</p>
            </div>
        """, unsafe_allow_html=True)
