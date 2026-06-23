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
# 🎨 DISEÑO OSCURO PREMIUM + INYECCIÓN PWA MOVIL
# =======================================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fondo Gris Oscuro Asfalto */
        .stApp {
            background-color: #141619 !important;
            color: #FFFFFF !important;
        }
        
        /* Textos globales legibles */
        p, label, span, .stMarkdown {
            color: #E2E8F0 !important;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
        }
        
        /* Títulos Mostaza */
        h1, h2, h3, h4, .mostaza-text {
            color: #E5A93C !important;
            font-weight: 700 !important;
        }
        
        /* Banner Principal */
        .header-container {
            background-color: #1F2327;
            padding: 22px;
            border-radius: 16px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #343A40;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
        }
        
        /* Adaptabilidad en Celulares (Cuadrícula táctil) */
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
        
        /* Botones tipo Cápsula */
        div.stButton > button {
            background-color: #1F2327 !important;
            color: #FFFFFF !important;
            border: 1px solid #495057 !important;
            border-radius: 25px !important;
            padding: 10px 15px !important;
            font-weight: 600 !important;
            width: 100% !important;
            min-height: 52px !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        /* Iluminación de Selección Activa */
        div.stButton > button:hover, div.stButton > button:focus {
            background-color: #E5A93C !important;
            color: #141619 !important;
            border-color: #E5A93C !important;
            box-shadow: 0px 0px 15px rgba(229, 169, 60, 0.5) !important;
        }
    </style>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#141619">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/2897/2897818.png">

    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('data:text/javascript;base64,Z2xvYmFsVGhpcy5hZGRFdmVudExpc3RlbmVyKCdmeXRjaCcsIGV2ID0+IGV2LnJlc3BvbmRXaXRoKGZldGNoKGV2LnJlcXVlc3QpKSk7')
            .then(() => console.log('PWA Logística Activa'));
        }
    </script>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 GESTIÓN DE ACCESO
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #E5A93C; margin-top:50px;'>🔐 Acceso al Sistema Logístico</h2>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        user_input = st.text_input("Usuario Corporativo:")
        pass_input = st.text_input("Contraseña de Acceso:", type="password")
        if st.button("Ingresar al Panel", use_container_width=True):
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
LISTA_ADMINS = ["larry", "supervisor", "admin", "piero pezo"] 
es_admin_o_super = user_activo.lower().strip() in LISTA_ADMINS

st.markdown(f"""
    <div class="header-container">
        <h1 style="color: #E5A93C; margin:0; font-size:26px;">🏢 CONSORCIO SAN MIGUEL</h1>
        <div style="color:#A5A5A5; font-size:13px; margin-top:6px;">Usuario: <span style="color:#E5A93C; font-weight:bold;">{user_activo}</span></div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 BARRA DE NAVEGACIÓN EN PANTALLA TÁCTIL
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
            if "Stock" in nombre_tecnico_menu: st.session_state.menu_actual = "Stock Consolidados"
            elif "Movimientos" in nombre_tecnico_menu: st.session_state.menu_actual = "Movimientos (Kardex)"
            elif "Auditoría" in nombre_tecnico_menu: st.session_state.menu_actual = "Auditoría de Terreno"
            elif "Ajustes" in nombre_tecnico_menu: st.session_state.menu_actual = "Ajustes del Sistema"
            else: st.session_state.menu_actual = nombre_tecnico_menu
            st.rerun()

st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border-color:#2D2D2D;'>", unsafe_allow_html=True)

# =======================================================================
# 🔌 ENRUTADOR SEGURO
# =======================================================================
sh = db.conectar_sheets()

if st.session_state.autenticado:
    if st.session_state.menu_actual == "Inicio":
        try: home.render(sh)
        except TypeError: home.render()
    elif st.session_state.menu_actual == "Panel de Control": dashboard.render(sh)
    elif st.session_state.menu_actual == "Stock Consolidados": reporte_stock.render(sh)
    elif st.session_state.menu_actual == "Movimientos (Kardex)": movimientos.render(sh)
    elif st.session_state.menu_actual == "Auditoría de Terreno": auditoria.render(sh)  
    elif st.session_state.menu_actual == "Ajustes del Sistema": ajustes.render(sh)

st.markdown("---")
if st.button("🚪 Cerrar Sesión del Sistema", type="secondary", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
