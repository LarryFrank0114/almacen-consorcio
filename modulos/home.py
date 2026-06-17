import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh):
    st.markdown("## Bienvenid@ al Panel de Control Logístico")
    st.markdown("Consorcio San Miguel — Gestión de Materiales e Infraestructura Externa.")
    st.markdown("---")
    
    # Intentar cargar la pestaña de anuncios desde Sheets de forma persistente
    try:
        ws_anuncios = sh.worksheet("anuncios")
        df_anuncios = pd.DataFrame(ws_anuncios.get_all_records())
    except:
        df_anuncios = pd.DataFrame(columns=["Fecha", "Autor", "Titulo", "Contenido"])

    # REGISTRO EXCLUSIVO PARA LARRY RODRIGUEZ
    if "Larry" in st.session_state.username:
        with st.expander("📢 Panel de Comandancia: Publicar Nuevo Anuncio / Noticia"):
            with st.form("form_anuncio", clear_on_submit=True):
                titulo = st.text_input("Título del Comunicado:")
                contenido = st.text_area("Cuerpo del Mensaje / Instrucciones Técnicas:")
                if st.form_submit_button("Lanzar Anuncio a toda la Red"):
                    if titulo and contenido:
                        nueva_fila = [datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.username, titulo, contenido]
                        try:
                            sh.worksheet("anuncios").append_row(nueva_fila)
                            st.success("Anuncio publicado con éxito en la portada de toda la cuadrilla.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar anuncio: {e}")
                    else:
                        st.warning("Por favor completa los campos antes de enviar.")

    # Renderizar los anuncios guardados cronológicamente inverso (más nuevo primero)
    st.markdown("### 📰 Comunicados y Novedades Operativas")
    if not df_anuncios.empty:
        df_anuncios = df_anuncios.iloc[::-1]  # Invertir orden
        for _, row in df_anuncios.head(5).iterrows():
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 5px solid #F57C00; border-radius: 6px; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #0B2545;">{row['Titulo']}</h4>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">⏳ {row['Fecha']} — Publicado por: <b>{row['Autor']}</b></p>
                <p style="margin: 10px 0 0 0; font-size: 14px; color: #333;">{row['Contenido']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay anuncios vigentes o alertas globales publicadas en este momento.")
