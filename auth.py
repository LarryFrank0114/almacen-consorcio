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
                    st.session_state.username = "Larry Rodriguez - Jefe de Almacenes Externos"
                    st.rerun()
                elif usuario.lower() == "supervision" and contraseña == "super123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Supervisor"
                    st.session_state.username = "Supervisor de Guardia SEDAPAL"
                    st.rerun()
                elif usuario.lower() == "piero" and contraseña == "piero123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.session_state.username = "Piero Pezo - Encargado Almacén 10"
                    st.rerun()
                elif usuario.lower() == "marcial" and contraseña == "marcial123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.session_state.username = "Marcial Huayta - Encargado Almacén 08"
                    st.rerun()
                elif usuario.lower() == "gregorio" and contraseña == "gregoriol123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.session_state.username = "Gregorio Rodriguez - Almacén 01"
                    st.rerun()
                elif usuario.lower() == "kike" and contraseña == "kike123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.session_state.username = "Enrique Sanchez - Encargado Almacén 06"
                    st.rerun()
                else:
                    st.error("❌ Usuario o Contraseña no válidos.")
