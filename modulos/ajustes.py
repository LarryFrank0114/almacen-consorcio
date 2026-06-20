import streamlit as st

def render(sh):
    st.markdown("<h2 style='color: #E5A93C;'>⚙️ Ajustes del Sistema</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A5A5A5;'>Módulo de configuración global e infraestructura de datos.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # =======================================================================
    # 🔒 INTERCEPCIÓN DE SEGURIDAD (CORRECCIÓN CONTRA ATTRIBUTEERROR)
    # =======================================================================
    # Intentamos obtener el rol de forma segura, si no existe usamos "Operador"
    user_role = st.session_state.get("user_role", "Operador")
    user_activo = st.session_state.get("username", "").lower().strip()
    
    LISTA_ADMINS = ["larry", "supervisor", "admin", "piero pezo"]

    # Si no cuenta con el rol explícito, pero está en la lista blanca de admins, le damos acceso
    if user_role != "Administrador" and user_activo not in LISTA_ADMINS:
        st.error("⛔ No cuentas con los permisos administrativos necesarios para modificar los Ajustes del Sistema.")
        st.stop()

    # =======================================================================
    # 🛠️ CONTENIDO DE LAS CONFIGURACIONES (MUESTRA O REEMPLAZA CON TU LÓGICA)
    # =======================================================================
    st.markdown("""
        <div style='background-color: #1F2327; padding: 20px; border-radius: 12px; border: 1px solid #343A40; margin-bottom: 20px;'>
            <h4 style='color: #E5A93C; margin-top:0;'>🔧 Estado de las Conexiones</h4>
            <p style='color: #E2E8F0; margin-bottom:0;'>🟢 Sincronización activa con Google Sheets Core API.</p>
        </div>
    """, unsafe_allow_html=True)

    tabs_ajustes = st.tabs(["👥 Gestión de Usuarios", "🏢 Sedes y Almacenes", "💾 Backups & Logística"])
    
    with tabs_ajustes[0]:
        st.subheader("Control de Usuarios Registrados")
        st.info("Aquí podrás añadir o remover credenciales de personal de campo próximamente.")
        # Agrega aquí tus inputs para bases de usuarios o roles de Sheets...

    with tabs_ajustes[1]:
        st.subheader("Configuración de Sedes Externas")
        st.write("Configuración por defecto del mapeo físico de inventarios.")
        # Agrega aquí tus inputs para añadir almacenes...

    with tabs_ajustes[2]:
        st.subheader("Mantenimiento de la Base de Datos")
        if st.button("🔄 Forzar Limpieza de Caché de Datos"):
            st.cache_data.clear()
            st.success("¡Caché del sistema vaciada exitosamente!")
