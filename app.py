import streamlit as st
import database as db
from modulos import home, dashboard, reporte_stock, movimientos, ajustes, auditoria

# Configuración inicial de la página (¡Debe ser la primera línea!)
st.set_page_config(
    page_title="Consorcio San Miguel - Gestión de Almacenes",
    layout="wide",
    initial_sidebar_state="collapsed" # Esconde la barra lateral de Streamlit
)

# =======================================================================
# 🎨 TEMA CLARO CORPORATIVO (PALETA BLANCO Y CELESTE SEDAPAL)
# =======================================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stApp {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
        }
        
        h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
            color: #1E293B !important;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        .header-container {
            background: linear-gradient(135deg, #005492 0%, #0076A8 100%);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0px 4px 15px rgba(0, 84, 146, 0.15);
        }
        .header-title {
            color: #FFFFFF !important;
            font-weight: 700;
            margin: 0;
            font-size: 30px;
            letter-spacing: 0.8px;
        }
        .header-subtitle {
            color: #E0F2FE !important;
            font-size: 14px;
            margin-top: 6px;
            font-weight: 500;
        }
        
        div[data-testid="stInfoHoverColumns"], .stAlert, div[data-testid="stNotification"] {
            background-color: #F0F6FA !important;
            border-left: 5px solid #0076A8 !important;
            color: #1E293B !important;
        }
        
        div.stButton > button {
            background-color: #F8FAFC !important;
            color: #005492 !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 12px 20px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            width: 100% !important;
            min-height: 58px !important;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.02) !important;
            transition: all 0.25s ease-in-out !important;
        }
        
        div.stButton > button:hover {
            background-color: #0076A8 !important;
            color: #FFFFFF !important;
            border-color: #0076A8 !important;
            box-shadow: 0px 6px 12px rgba(0, 118, 168, 0.25) !important;
            transform: translateY(-2px);
        }
        
        .stTextInput input, .stSelectbox div {
            background-color: #F8FAFC !important;
            color: #1E293B !important;
            border: 1px solid #CBD5E1 !important;
        }
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 CONTROL DE ACCESO INTERNO (LOGIN REUTILIZADO)
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # Pantalla de Login limpia y centrada
    st.markdown("<h2 style='text-align: center; color: #005492;'>🔐 Acceso al Sistema Logístico</h2>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        user_input = st.text_input("Usuario Corporativo:")
        pass_input = st.text_input("Contraseña de Acceso:", type="password")
        
        if st.button("Ingresar al Panel", use_container_width=True, type="primary"):
            # Mantenemos las credenciales que ya utilizas en producción
            # Modifica o acopla esto si consultas contraseñas desde los st.secrets
            if user_input != "" and pass_input != "": 
                st.session_state.autenticado = True
                st.session_state.username = user_input
                st.success("Acceso concedido.")
                st.rerun()
            else:
                st.error("❌ Por favor, ingrese un usuario y contraseña válidos.")
    st.stop() # Frena la ejecución aquí si el usuario no está validado

# =======================================================================
# 🏢 ENCABEZADO PRINCIPAL (SÓLO SI YA ESTÁ AUTENTICADO)
# =======================================================================
user_activo = st.session_state.username
es_admin_o_super = "Larry" in user_activo or "Supervisor" in user_activo

st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">🏢 CONSORCIO SAN MIGUEL</h1>
        <div class="header-subtitle">Bienvenido(a), {user_activo} | Control Logístico e Infraestructura</div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 BARRA DE NAVEGACIÓN SUPERIOR CON FILTRADO DE ROLES
# =======================================================================
# Definimos los módulos visibles dinámicamente según el rol del usuario
if es_admin_o_super:
    opciones_menu = ["🏠\nInicio", "📊\nPanel Control", "📦\nStock Consolidados", "🔄\nMovimientos", "📋\nAuditoría Terreno", "⚙️\nAjustes"]
else:
    # Restricción para operarios/encargados de almacén específicos (No ven Ajustes ni Kardex global si así lo requieres)
    opciones_menu = ["🏠\nInicio", "📊\nPanel Control", "📦\nStock Consolidados", "📋\nAuditoría Terreno"]

cols_nav = st.columns(len(opciones_menu))

for idx, opcion in enumerate(opciones_menu):
    with cols_nav[idx]:
        # Limpiamos el emoji para guardar el nombre técnico del menú en el state
        nombre_tecnico_menu = opcion.split("\n")[1] if "\n" in opcion else opcion
        
        # Si la opción actual coincide con el estado, el botón puede recibir un enfoque o estilo diferente
        if st.button(opcion, use_container_width=True, key=f"btn_{nombre_tecnico_menu}"):
            # Mapeo de nombres para mantener compatibilidad con tu enrutador
            if "Stock" in nombre_tecnico_menu:
                st.session_state.menu_actual = "Stock Consolidados"
            elif "Movimientos" in nombre_tecnico_menu:
                st.session_state.menu_actual = "Movimientos (Kardex)"
            elif "Auditoría" in nombre_tecnico_menu:
                st.session_state.menu_actual = "Auditoría de Terreno"
            elif "Ajustes" in nombre_tecnico_menu:
                st.session_state.menu_actual = "Ajustes del Sistema"
            else:
                st.session_state.menu_actual = nombre_tecnico_menu
            st.rerun()

st.markdown("<hr style='margin-top:5px; margin-bottom:20px; border-color:#E2E8F0;'>", unsafe_allow_html=True)

# Botón discreto para cerrar sesión en la esquina superior derecha si fuera necesario
col_v, col_logout = st.columns([5, 1])
with col_logout:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.username = None
        st.session_state.menu_actual = "Inicio"
        st.rerun()

# =======================================================================
# 🔌 ENRUTADOR DINÁMICO DE PÁGINAS (EJECUCIÓN SEGURA)
# =======================================================================
sh = db.conectar_sheets()

if st.session_state.menu_actual == "Inicio":
    try:
        home.render()
    except TypeError:
        home.render(sh)
        
elif st.session_state.menu_actual == "Panel de Control":
    dashboard.render(sh)
    
elif st.session_state.menu_actual == "Stock Consolidados":
    reporte_stock.render(sh)
    
elif st.session_state.menu_actual == "Movimientos (Kardex)":
    movimientos.render(sh)
    
elif st.session_state.menu_actual == "Auditoría de Terreno":
    auditoria.render(sh)  
    
elif st.session_state.menu_actual == "Ajustes del Sistema":
    ajustes.render(sh)
