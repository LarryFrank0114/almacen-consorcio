import streamlit as st
import auth as au     
import database as db  

# Importamos los nuevos módulos de la carpeta 'modulos'
from modulos import dashboard, reporte_stock, movimientos, ajustes

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS MINIMALISTAS
# ==========================================
st.set_page_config(
    page_title="Consorcio San Miguel",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Minimalista: Botones grandes, rectangulares y redondeados
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        /* Cabecera limpia sin íconos */
        .header-minimal {
            background-color: #0B2545;
            padding: 20px 30px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-title { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
        .header-user { font-size: 13px; opacity: 0.9; font-weight: 500; }
        
        /* Estilos globales para inputs y botones de Streamlit */
        div.stButton > button {
            background-color: #F57C00 !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
            border-radius: 8px !important; /* Bordes redondeados sutiles y modernos */
            padding: 0.6rem 2rem !important;
            font-size: 15px !important;
            width: 100%;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            background-color: #E65100 !important;
            transform: translateY(-1px);
        }
        
        /* Customización del Segmented Control para que parezcan botones rectangulares grandes */
        div[data-testid="stSegmentedControl"] button {
            padding: 12px 24px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
            background-color: white !important;
            color: #0B2545 !important;
        }
        div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
            background-color: #0B2545 !important;
            color: white !important;
            border-color: #0B2545 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Verificar sesión con tu auth.py
au.verificar_sesion()

if not st.session_state.logged_in:
    au.login_form()
    st.stop()

# Conexión a Base de Datos
sh = db.conectar_sheets()
if sh is None:
    st.error("Error de comunicación con el servidor central.")
    st.stop()

# ==========================================
# CABECERA MINIMALISTA
# ==========================================
st.markdown(f"""
    <div class="header-minimal">
        <div class="header-title">CONSORCIO SAN MIGUEL</div>
        <div class="header-user">{st.session_state.username} — [{st.session_state.user_role}]</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# MENÚ DE NAVEGACIÓN SUPERIOR EN BLOQUES (SIN ÍCONOS)
# ==========================================
opciones_menu = ["Dashboard", "Reporte Stock", "Movimientos", "Ajustes"]

opcion_seleccionada = st.segmented_control(
    "Menu Navegacion",
    options=opciones_menu,
    default="Dashboard",
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ENRUTADOR DE MÓDULOS EN CARPETA SEPARADA
# ==========================================
if opcion_seleccionada == "Dashboard":
    dashboard.render(sh)
elif opcion_seleccionada == "Reporte Stock":
    reporte_stock.render(sh)
elif opcion_seleccionada == "Movimientos":
    movimientos.render(sh)
elif opcion_seleccionada == "Ajustes":
    ajustes.render(sh)

# Botón de salida elegante en la parte baja
st.markdown("<br><hr>", unsafe_allow_html=True)
col_out1, col_out2, col_out3 = st.columns([1, 1, 1])
with col_out2:
    if st.button("Salir del Sistema", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = ""
        st.rerun()
