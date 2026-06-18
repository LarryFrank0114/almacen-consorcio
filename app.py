import streamlit as st
import database as db

# Configuración obligatoria de la página de Streamlit (Debe ser la primera línea de ejecución)
st.set_page_config(
    page_title="Consorcio San Miguel",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # 🌎 1. Inicialización y Gestión bilingüe del estado de la sesión
    if "idioma" not in st.session_state:
        st.session_state.idioma = "es"
        
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    # Diccionario local para la pantalla de inicio de sesión
    textos_auth = {
        "es": {
            "bienvenida": "🔒 Control de Acceso · Almacén",
            "usuario": "Usuario",
            "clave": "Contraseña",
            "btn_ingresar": "Ingresar Sistema",
            "error_auth": "❌ Usuario o contraseña incorrectos.",
            "logout": "🚪 Cerrar Sesión"
        },
        "zh": {
            "bienvenida": "🔒 访问控制 · 仓库",
            "usuario": "用户",
            "clave": "密码",
            "btn_ingresar": "登录系统",
            "error_auth": "❌ 用户名 or 密码错误。",
            "logout": "🚪 注销登录"
        }
    }

    # 🌎 Selector de Idioma exclusivo para la pantalla de Login (Luego el dashboard tomará el control)
    if not st.session_state.logged_in:
        idioma_inicial = st.sidebar.selectbox("🌐 Language / 語言", ["Español", "繁體中文 (Chino Tradicional)"], key="lang_login")
        st.session_state.idioma = "es" if "Español" in idioma_inicial else "zh"

    lang_auth = textos_auth[st.session_state.idioma]

    # 🔐 2. Sistema de Autenticación de Usuarios
    if not st.session_state.logged_in:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.subheader(lang_auth["bienvenida"])
            with st.form("formulario_login"):
                user_input = st.text_input(lang_auth["usuario"], placeholder="Ej. Larry Frank")
                pass_input = st.text_input(lang_auth["clave"], type="password")
                btn_submit = st.form_submit_with_button_options if hasattr(st, "form_submit_with_button_options") else st.form_submit_button(lang_auth["btn_ingresar"])
                
                if btn_submit:
                    # Base de datos local de usuarios autorizados
                    usuarios_validos = {
                        "Larry Frank": "sm2026",
                        "Supervisor Almacen": "almacen2026",
                        "Admin": "admin99"
                    }
                    
                    if user_input in usuarios_validos and usuarios_validos[user_input] == pass_input:
                        st.session_state.logged_in = True
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error(lang_auth["error_auth"])
        return

    # 📊 3. Conexión segura con la Base de Datos en Google Sheets (Línea 71 corregida)
    sh = db.conectar_sheets()
    if not sh:
        st.error("❌ Error crítico: No se pudo establecer la comunicación con el servidor de Google Sheets. Verifica los secrets.")
        return
