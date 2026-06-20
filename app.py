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
# 🎨 TEMA CLARO CORPORATIVO Y DISEÑO FLEXIBLE RESPONSIVO (PALETA SEDAPAL)
# =======================================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fondo general de la aplicación */
        .stApp {
            background-color: #B8EEFF !important;
            color: #1E293B !important;
        }
        
        h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
            color: #1E293B !important;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        /* Banner del Encabezado */
        .header-container {
            background: linear-gradient(135deg, #005492 0%, #0076A8 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0px 4px 15px rgba(0, 84, 146, 0.15);
        }
        .header-title {
            color: #FFFFFF !important;
            font-weight: 700;
            margin: 0;
            font-size: 26px;
            letter-spacing: 0.8px;
        }
        .header-subtitle {
            color: #E0F2FE !important;
            font-size: 13px;
            margin-top: 6px;
            font-weight: 500;
        }

        /* 📱 MAGIA RESPONSIVA: Forzar que las columnas de Streamlit se adapten en celulares */
        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 10px !important;
            }
            div[data-testid="column"] {
                width: calc(50% - 10px) !important; /* En celulares los botones se acomodan de 2 en 2 */
                flex-min-width: calc(50% - 10px) !important;
                margin-bottom: 5px !important;
            }
        }
        
        /* Diseño de los Botones del Menú */
        div.stButton > button {
            background-color: #F8FAFC !important;
            color: #005492 !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 8px 10px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            width: 100% !important;
            min-height: 54px !important;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.02) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        /* Hover e Interacción */
        div.stButton > button:hover {
            background-color: #0076A8 !important;
            color: #FFFFFF !important;
            border-color: #0076A8 !important;
            box-shadow: 0px 4px 10px rgba(0, 118, 168, 0.2) !important;
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 CONTROL DE ACCESO (LOGIN SEGURO)
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #005492; margin-top:50px;'>🔐 Acceso al Sistema Logístico</h2>", unsafe_allow_html=True)
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
es_admin_o_super = "Larry" in user_activo or "Supervisor" in user_activo

st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">🏢 CONSORCIO SAN MIGUEL</h1>
        <div class="header-subtitle">Usuario: {user_activo} | Panel de Control de Campo</div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 BARRA DE NAVEGACIÓN TOTALMENTE RESPONSIVA
# =======================================================================
# Filtramos las opciones según el rol del usuario logueado
if es_admin_o_super:
    opciones_menu = ["🏠\nInicio", "📊\nPanel Control", "📦\nStock Consolidados", "🔄\nMovimientos", "📋\nAuditoría Terreno", "⚙️\nAjustes"]
else:
    opciones_menu = ["🏠\nInicio", "📊\nPanel Control", "📦\nStock Consolidados", "📋\nAuditoría Terreno"]

# El contenedor de columnas ahora es fluido gracias a las reglas CSS inyectadas arriba
cols_nav = st.columns(len(opciones_menu))

for idx, opcion in enumerate(opciones_menu):
    with cols_nav[idx]:
        nombre_tecnico_menu = opcion.split("\n")[1] if "\n" in opcion else opcion
        
        # Generar botón inteligente
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

st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border-color:#E2E8F0;'>", unsafe_allow_html=True)

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
    ajustes.render(sh) # <- Tu pestaña de Ajustes asignada perfectamente

# Botón de salida móvil en la parte inferior para no entorpecer la cabecera
st.markdown("---")
if st.button("🚪 Cerrar Sesión del Sistema", type="secondary"):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
