import streamlit as st
import database as db
from modulos import home, dashboard, reporte_stock, movimientos, ajustes, auditoria

# Configuración inicial de la página
st.set_page_config(
    page_title="Consorcio San Miguel - Gestión de Almacenes",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =======================================================================
# 🎨 DISEÑO DARK PREMIUM & RESPONSIVO (INSPIRADO EN image_87f7fc.png)
# =======================================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fondo general ultra oscuro */
        .stApp {
            background-color: #121212 !important;
            color: #E0E0E0 !important;
        }
        
        /* Forzar color de textos globales y títulos */
        h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
            color: #E0E0E0 !important;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        /* Títulos destacados en amarillo dorado */
        h1, h2, h3, .gold-text {
            color: #FFC107 !important;
        }
        
        /* Banner del Encabezado estilo Tarjeta Neumórfica Oscura */
        .header-container {
            background-color: #1E1E1E;
            padding: 22px;
            border-radius: 16px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #2D2D2D;
            box-shadow: inset 1px 1px 1px rgba(255,255,255,0.05), 0px 4px 15px rgba(0,0,0,0.5);
        }
        .header-title {
            color: #FFC107 !important;
            font-weight: 700;
            margin: 0;
            font-size: 26px;
            letter-spacing: 1px;
        }
        .header-subtitle {
            color: #AAAAAA !important;
            font-size: 13px;
            margin-top: 6px;
            font-weight: 500;
        }

        /* 📱 Adaptabilidad Móvil del Menú */
        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 12px !important;
            }
            div[data-testid="column"] {
                width: calc(50% - 6px) !important;
                flex-min-width: calc(50% - 6px) !important;
                margin-bottom: 4px !important;
            }
        }
        
        /* Botones del Menú - Estilo Cápsula Redondeada */
        div.stButton > button {
            background-color: #1E1E1E !important;
            color: #E0E0E0 !important;
            border: 1px solid #333333 !important;
            border-radius: 25px !important; /* Bordes bien redondeados como la imagen */
            padding: 10px 15px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            width: 100% !important;
            min-height: 52px !important;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        /* Hover: Transición a Amarillo Dorado Brillante con letras oscuras */
        div.stButton > button:hover {
            background-color: #FFC107 !important;
            color: #121212 !important;
            border-color: #FFC107 !important;
            box-shadow: 0px 0px 15px rgba(255, 193, 7, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Inputs, Cajas y Selectores adaptados al modo oscuro */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
        }
        
        /* Estilo para los contenedores/tarjetas informativas de los módulos */
        div[data-testid="stInfoHoverColumns"], .stAlert, div[data-testid="stNotification"], .element-container div.stMarkdown {
            background-color: #1E1E1E !important;
            color: #E0E0E0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 CONTROL DE ACCESO (LOGIN SEGURO)
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #FFC107; margin-top:50px;'>🔐 Acceso al Sistema Logístico</h2>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        user_input = st.text_input("Usuario Corporativo:")
        pass_input = st.text_input("Contraseña de Acceso:", type="password")
        if st.button("Ingresar al Panel", use_container_width=True, type="primary"):
            if user_input != "" and pass_input != "": 
                st.session_state.autenticado = True
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("❌ Por favor, ingrese credenciales válidas.")
    st.stop()

# =======================================================================
# 🏢 ENCABEZADO PRINCIPAL
# =======================================================================
user_activo = st.session_state.username

# ⚙️ SOLUCIÓN PARA QUE VEAS EL BOTÓN DE AJUSTES: 
# Agrega aquí tu usuario exacto (ej. tu nombre o correo) dentro de la lista de administradores
LISTA_ADMINS = ["Larry", "Supervisor", "Admin", "admin", "Piero Pezo"] 
es_admin_o_super = any(admin in user_activo for admin in LISTA_ADMINS)

st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">🏢 CONSORCIO SAN MIGUEL</h1>
        <div class="header-subtitle">Usuario: <span style="color:#FFC107;">{user_activo}</span> | Panel de Control de Campo</div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 BARRA DE NAVEGACIÓN RESPONSIVA
# =======================================================================
if es_admin_o_super:
    opciones_menu = ["🏠\nInicio", "📊\nPanel Control", "📦\nStock Consolidados", "🔄\nMovimientos", "📋\nAuditoría Terreno", "⚙️\nAjustes"]
else:
    opciones_menu = ["🏠\nInicio", "📊\nPanel Control", "📦\nStock Consolidados", "📋\nAuditoría Terreno"]

cols_nav = st.columns(len(opciones_menu))

for idx, opcion in enumerate(opciones_menu):
    with cols_nav[idx]:
        nombre_tecnico_menu = opcion.split("\n")[1] if "\n" in opcion else opcion
        
        if st.button(opcion, use_container_width=True, key=f"btn_{nombre_tecnico_menu}"):
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

st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border-color:#2D2D2D;'>", unsafe_allow_html=True)

# =======================================================================
# 🔌 ENRUTADOR DINÁMICO DE PÁGINAS
# =======================================================================
sh = db.conectar_sheets()

if st.session_state.menu_actual == "Inicio":
    try: home.render()
    except TypeError: home.render(sh)
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

# Botón de cierre de sesión integrado al estilo oscuro en la parte baja
st.markdown("---")
if st.button("🚪 Cerrar Sesión del Sistema", type="secondary"):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
