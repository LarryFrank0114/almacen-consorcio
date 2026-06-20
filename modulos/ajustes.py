import streamlit as st

def render(sh):
    st.markdown("<h2 style='color: #E5A93C;'>⚙️ Ajustes del Sistema</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A5A5A5;'>Módulo de configuración global e infraestructura de datos.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    user_role = st.session_state.get("user_role", "Operador")
    user_activo = st.session_state.get("username", "").lower().strip()
    
    LISTA_ADMINS = ["larry", "supervisor", "admin", "piero pezo"]

    if user_role != "Administrador" and user_activo not in LISTA_ADMINS:
        st.error("⛔ No cuentas con los permisos administrativos necesarios.")
        st.stop()

    st.markdown("""
        <div style='background-color: #1F2327; padding: 20px; border-radius: 12px; border: 1px solid #343A40; margin-bottom: 20px;'>
            <h4 style='color: #E5A93C; margin-top:0;'>🔧 Estado del Núcleo</h4>
            <p style='color: #E2E8F0; margin-bottom:0;'>🟢 Conexión estable con la API de Google Sheets.</p>
        </div>
    """, unsafe_allow_html=True)

    tabs_ajustes = st.tabs(["👥 Gestión de Usuarios", "🔄 Mantenimiento"])
    
    with tabs_ajustes[0]:
        st.subheader("Control de Personal Autorizado")
        st.info("Módulo en desarrollo para adición de firmas electrónicas en campo.")

    with tabs_ajustes[1]:
        st.subheader("Base de Datos")
        if st.button("🔄 Vaciar Memoria Caché del Sistema"):
            st.cache_data.clear()
            st.success("¡Caché optimizada y limpia!")
