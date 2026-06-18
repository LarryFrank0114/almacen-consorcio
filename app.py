import streamlit as st
import database as db

# 🌐 Configuración obligatoria de la página (DEBE SER LA PRIMERA LÍNEA DE STREAMLIT)
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
            "error_auth": "❌ 用户名 o 密码错误。",
            "logout": "🚪 注销登录"
        }
    }

    # 🌎 Selector de Idioma exclusivo para la pantalla de Login
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
                btn_submit = st.form_submit_button(lang_auth["btn_ingresar"])
                
                if btn_submit:
                    # Base de datos de usuarios autorizados
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

    # 📊 3. Conexión segura con la Base de Datos en Google Sheets
    sh = db.conectar_sheets()
    if not sh:
        st.error("❌ Error crítico: No se pudo establecer la comunicación con el servidor de Google Sheets. Verifica los secrets.")
        return

    # 🧭 4. Menú de Navegación Lateral y Enrutamiento de Módulos
    st.sidebar.markdown(f"👤 **{st.session_state.username}**")
    
    # Menú dinámico bilingüe de navegación
    opciones_menu = {
        "es": ["📊 Cuadro de Control (Dashboard)", "📥 Registro de Movimientos", "📸 Auditoría Fotográfica"],
        "zh": ["📊 仪表板 (Dashboard)", "📥 变动登记", "📸 照片审计"]
    }
    
    menu_seleccionado = st.sidebar.radio(
        "🗂️ Menú / 菜单", 
        opciones_menu[st.session_state.idioma]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button(lang_auth["logout"]):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    # 🚀 5. Renderizado del módulo seleccionado
    # Módulo Dashboard (Se alimenta de modulos/dashboard.py y modulos/estilos.py)
    if "Dashboard" in menu_seleccionado or "仪表板" in menu_seleccionado:
        from modulos import dashboard
        dashboard.render(sh)
        
    # Módulo de Transacciones (Ingresos / Egresos)
    elif "Movimientos" in menu_seleccionado or "变动登记" in menu_seleccionado:
        st.title("📥 Registro de Movimientos / 变动登记")
        st.info("Espacio reservado para el formulario de ingresos, egresos e inventarios.")
        
    # Módulo de Auditoría Fotográfica
    elif "Fotográfica" in menu_seleccionado or "照片审计" in menu_seleccionado:
        st.title("📸 Auditoría Fotográfica / 照片审计")
        st.info("Espacio para la visualización y captura de imágenes Base64 guardadas en la pestaña 'fotos'.")

if __name__ == "__main__":
    main()
