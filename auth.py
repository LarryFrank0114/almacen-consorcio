import streamlit as st

def verificar_sesion():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = ""

def login_form():
    st.markdown("<h2 style='text-align: center; color:#1E3A8A; font-weight:800;'>🏗️ CONSORCIO SAN MIGUEL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#64748B;'>Saneamiento 'Nueva Rinconada' — SEDAPAL</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.form("Login"):
            st.markdown("### 🔐 Acceso al Sistema de Almacenes")
            usuario = st.text_input("Usuario").strip()
            contraseña = st.text_input("Contraseña", type="password")
            btn = st.form_submit_button("Ingresar al Sistema")
            
            if btn:
                if usuario.lower() == "larry" and contraseña == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.session_state.username = "Larry Frank Rodriguez (Jefe de Almacenes)"
                    st.rerun()
                elif usuario.lower() == "supervisor" and contraseña == "super123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Supervisor"
                    st.session_state.username = "Supervisor de Guardia SEDAPAL"
                    st.rerun()
                else:
                    st.error("❌ Usuario o Contraseña no válidos.")
