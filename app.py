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
# 🎨 DISEÑO ULTRA PREMIUM (FONDO OSCURO, TEXTOS MOSTAZA Y SELECCIÓN BRILLANTE)
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
        
        /* Forzar color de textos globales y etiquetas */
        h4, h5, h6, p, label, span, .stMarkdown {
            color: #E0E0E0 !important;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        /* 🌟 Títulos principales y destacados en Amarillo Mostaza */
        h1, h2, h3, .mostaza-text {
            color: #E5A93C !important;  /* Amarillo Mostaza Premium */
            font-weight: 700 !important;
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
            color: #E5A93C !important;
            font-weight: 700;
            margin: 0;
            font-size: 26px;
            letter-spacing: 1px;
        }
        .header-subtitle {
            color: #A5A5A5 !important;
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
            color: #D5D5D5 !important;
            border: 1px solid #3A3A3A !important;
            border-radius: 25px !important;
            padding: 10px 15px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            width: 100% !important;
            min-height: 52px !important;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.4) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        /* ✨ EFECTO EN HOVER / SELECCIÓN: Color Mostaza Brillante Eléctrico */
        div.stButton > button:hover, div.stButton > button:focus {
            background-color: #E5A93C !important;
            color: #121212 !important;
            border-color: #FFC86B !important;
            box-shadow: 0px 0px 18px rgba(229, 169, 60, 0.6) !important;
            transform: translateY(-2px);
        }
        
        /* Inputs, Cajas de texto y Selectores adaptados al modo oscuro */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
            border: 1px solid #3A3A3A !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 CONTROL DE ACCESO (LOGIN SEGURO)
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #E5A93C; margin-top:50px;'>🔐 Acceso al Sistema Logístico</h2>", unsafe_allow_html=True)
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
# 🏢 ENCABEZADO PRINCIPAL (POST-LOGIN)
# =======================================================================
user_activo = st.session_state.username

# ⚙️ SOLUCIÓN DEFINITIVA DE ROLES (Insensible a mayúsculas/minúsculas):
LISTA_ADMINS = ["larry", "supervisor", "admin", "piero pezo"] 
es_admin_o_super = user_activo.lower().strip() in LISTA_ADMINS

st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">🏢 CONSORCIO SAN MIGUEL</h1>
        <div class="header-subtitle">Usuario: <span style="color:#E5A93C; font-weight:bold;">{user_activo}</span> | Panel de Control de Campo</div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 BARRA DE NAVEGACIÓN RESPONSIVA (AMARILLO MOSTAZA EN ACCIÓN)
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
    try: movimientos.render(sh)
    except NameError: movements.render(sh)
elif st.session_state.menu_actual == "Auditoría de Terreno":
    auditoria.render(sh)  
elif st.session_state.menu_actual == "Ajustes del Sistema":
    ajustes.render(sh)

# Botón de cierre de sesión integrado en la sección inferior
st.markdown("---")
if st.button("🚪 Cerrar Sesión del Sistema", type="secondary"):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
