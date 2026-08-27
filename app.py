# app.py
import streamlit as st
from auth import AuthSystem
from email_service import EmailService
import time

# Configuración de la página
st.set_page_config(
    page_title="Almacen Consorcio",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar servicios
auth_system = AuthSystem()
email_service = EmailService()

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .verification-code {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 10px;
        background: #f0f8f0;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        transform: scale(0.98);
        transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

def show_header():
    """Muestra el encabezado de la aplicación"""
    st.markdown("""
        <div class="main-header">
            <h1>🏪 Sistema de Gestión de Almacén</h1>
            <p>Control de inventario y gestión de productos</p>
        </div>
    """, unsafe_allow_html=True)

def login_page():
    """Página de inicio de sesión"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("🔐 Iniciar Sesión")
        
        with st.form("login_form"):
            email = st.text_input("📧 Correo Electrónico", placeholder="tu@email.com")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            with col_btn2:
                st.form_submit_button("Registrarse", on_click=show_register, use_container_width=True)
        
        if submitted:
            if email and password:
                user, message = auth_system.login(email, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Por favor, completa todos los campos")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón para recuperar contraseña
        with st.expander("🔑 ¿Olvidaste tu contraseña?"):
            st.info("Contacta al administrador para restablecer tu contraseña")

def show_register():
    """Muestra la página de registro"""
    st.session_state['show_register'] = True

def register_page():
    """Página de registro de nuevos usuarios"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("📝 Registro de Usuario")
        
        # Paso 1: Datos del usuario
        with st.form("register_form"):
            nombre = st.text_input("👤 Nombre Completo", placeholder="Juan Pérez")
            email = st.text_input("📧 Correo Electrónico", placeholder="tu@email.com")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            confirm_password = st.text_input("🔑 Confirmar Contraseña", type="password", placeholder="Repite tu contraseña")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("Registrarse", use_container_width=True)
            with col_btn2:
                st.form_submit_button("Volver al Login", on_click=back_to_login, use_container_width=True)
        
        if submitted:
            if not all([nombre, email, password, confirm_password]):
                st.warning("⚠️ Por favor, completa todos los campos")
            elif len(password) < 6:
                st.warning("⚠️ La contraseña debe tener al menos 6 caracteres")
            elif password != confirm_password:
                st.warning("⚠️ Las contraseñas no coinciden")
            else:
                # Generar código de verificación
                verification_code = email_service.generate_verification_code()
                
                # Registrar usuario
                success, message = auth_system.register_user(email, nombre, password, verification_code)
                
                if success:
                    # Enviar correo con código
                    if email_service.send_verification_email(email, verification_code):
                        st.session_state['pending_verification'] = {
                            'email': email,
                            'code': verification_code
                        }
                        st.session_state['show_verification'] = True
                        st.success("✅ ¡Registro exitoso! Se ha enviado un código a tu correo")
                        st.rerun()
                    else:
                        st.error("❌ Error al enviar el correo de verificación. Intenta nuevamente")
                else:
                    st.error(f"❌ {message}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def verification_page():
    """Página de verificación de código"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("🔐 Verificación de Correo")
        
        if 'pending_verification' in st.session_state:
            email = st.session_state['pending_verification']['email']
            st.info(f"📧 Se ha enviado un código de verificación a: **{email}**")
            
            with st.form("verification_form"):
                code_input = st.text_input("📱 Código de Verificación", 
                                         placeholder="Ingresa el código de 6 dígitos",
                                         max_chars=6)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("Verificar Código", use_container_width=True)
                with col_btn2:
                    st.form_submit_button("Reenviar Código", on_click=resend_code, use_container_width=True)
            
            if submitted:
                if code_input:
                    success, message = auth_system.verify_user_code(email, code_input)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        # Limpiar estado y redirigir a login
                        del st.session_state['pending_verification']
                        del st.session_state['show_verification']
                        st.info("🎉 ¡Tu cuenta ha sido verificada! Ahora puedes iniciar sesión")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Por favor, ingresa el código de verificación")
        else:
            st.warning("No hay una verificación pendiente")
            if st.button("Volver al Login"):
                back_to_login()
        
        st.markdown('</div>', unsafe_allow_html=True)

def resend_code():
    """Reenvía el código de verificación"""
    if 'pending_verification' in st.session_state:
        email = st.session_state['pending_verification']['email']
        success, message = auth_system.resend_verification_code(email)
        if success:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")

def back_to_login():
    """Vuelve a la página de login"""
    keys_to_clear = ['show_register', 'show_verification', 'pending_verification']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def main_app():
    """Aplicación principal (después del login)"""
    st.title(f"🏪 Bienvenido, {st.session_state['user']['nombre']}!")
    st.write(f"📧 {st.session_state['user']['email']} | 👤 Rol: {st.session_state['user']['rol']}")
    
    # Aquí va el contenido principal de tu aplicación de almacén
    # Puedes mantener tu código existente de gestión de inventario
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Productos en Stock", "0", "0%")
    with col2:
        st.metric("🔄 Movimientos Hoy", "0", "0")
    with col3:
        st.metric("⚠️ Stock Bajo", "0", "0")
    
    # Espacio para tu contenido existente
    st.info("📋 Aquí puedes agregar tu sistema de gestión de inventario")
    
    # Botón de cierre de sesión
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['logged_in'] = False
        if 'user' in st.session_state:
            del st.session_state['user']
        st.rerun()

# Control de flujo principal
def main():
    # Inicializar estados de sesión
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if 'show_register' not in st.session_state:
        st.session_state['show_register'] = False
    
    if 'show_verification' not in st.session_state:
        st.session_state['show_verification'] = False
    
    # Navegación de páginas
    if st.session_state['logged_in']:
        main_app()
    elif st.session_state['show_verification']:
        verification_page()
    elif st.session_state['show_register']:
        register_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
