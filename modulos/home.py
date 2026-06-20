import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh):
    st.markdown("<h2 style='color: #E5A93C; text-align: center;'>📢 Comunicados y Novedades Operativas</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A5A5A5;'>Consorcio San Miguel — Gestión de Materiales e Infraestructura Externa.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        ws_anuncios = sh.worksheet("anuncios")
        datos = ws_anuncios.get_all_records()
        df_anuncios = pd.DataFrame(datos)
    except Exception as e:
        st.error(f"⚠️ No se pudo acceder a la pestaña 'anuncios' en Google Sheets: {e}")
        return

    user_activo = st.session_state.get("username", "Invitado").lower().strip()
    es_admin = user_activo in ["larry", "supervisor", "admin", "piero pezo"]

    # =======================================================================
    # 🛠️ GESTIÓN DE ANUNCIOS (ADMINISTRADORES)
    # =======================================================================
    if es_admin:
        with st.expander("⚙️ Panel de Administración de Comunicados (Publicar / Modificar)"):
            accion = st.radio("Elige una acción:", ["✨ Publicar Nuevo Anuncio", "✏️ Modificar / Eliminar Existente"], horizontal=True)
            
            if accion == "✨ Publicar Nuevo Anuncio":
                nuevo_titulo = st.text_input("Título del Comunicado:")
                nuevo_contenido = st.text_area("Cuerpo del Mensaje:")
                
                if st.button("🚀 Lanzar Anuncio Oficial", use_container_width=True):
                    if nuevo_titulo and nuevo_contenido:
                        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                        ws_anuncios.append_row([fecha_actual, user_activo, nuevo_titulo, nuevo_contenido])
                        st.success("¡Anuncio publicado!")
                        st.rerun()
            
            elif accion == "✏️ Modificar / Eliminar Existente" and not df_anuncios.empty:
                opciones_anuncios = df_anuncios.iloc[:, 2].tolist() if df_anuncios.shape[1] > 2 else []
                if opciones_anuncios:
                    anuncio_sel = st.selectbox("Selecciona el anuncio a modificar:", opciones_anuncios)
                    idx = opciones_anuncios.index(anuncio_sel)
                    fila_sheets = idx + 2
                    
                    edit_titulo = st.text_input("Editar Título:", value=df_anuncios.iloc[idx, 2])
                    edit_contenido = st.text_area("Editar Cuerpo:", value=df_anuncios.iloc[idx, 3])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("💾 Guardar Cambios", use_container_width=True):
                            ws_anuncios.update_cell(fila_sheets, 3, edit_titulo)
                            ws_anuncios.update_cell(fila_sheets, 4, edit_contenido)
                            st.success("¡Actualizado!")
                            st.rerun()
                    with c2:
                        if st.button("🗑️ Eliminar Anuncio", use_container_width=True, type="primary"):
                            ws_anuncios.delete_rows(fila_sheets)
                            st.warning("¡Eliminado!")
                            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # =======================================================================
    # 👀 VISTA PÚBLICA DE ANUNCIOS (ALTO CONTRASTE INTEGRADO)
    # =======================================================================
    if not df_anuncios.empty:
        df_anuncios.columns = [str(col).lower().strip() for col in df_anuncios.columns]
        
        for _, row in df_anuncios.iloc[::-1].iterrows():
            col_titulo = row.get('titulo', 'Sin Título')
            col_fecha = row.get('fecha', 'N/A')
            col_usuario = row.get('usuario', row.get('responsable', 'Sistema'))
            col_contenido = row.get('contenido', '')

            st.markdown(f"""
                <div style="background-color: #1F2327; padding: 22px; border-radius: 12px; border-left: 6px solid #E5A93C; margin-bottom: 18px; border: 1px solid #343A40; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                    <h3 style="margin: 0 0 6px 0; color: #E5A93C !important; font-size: 19px; font-weight:700;">{col_titulo}</h3>
                    <p style="margin: 0 0 14px 0; color: #A5A5A5 !important; font-size: 12px;">
                        ⏳ Registro: {col_fecha} &nbsp;|&nbsp; 👷 Responsable: <span style="color:#E5A93C; font-weight:bold;">{col_usuario}</span>
                    </p>
                    <div style="color: #FFFFFF !important; font-size: 14.5px; line-height: 1.6; white-space: pre-wrap;">{col_contenido}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay comunicados vigentes.")
