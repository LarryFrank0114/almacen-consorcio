import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import auth as au     
import database as db  
from modulos import home, dashboard, reporte_stock, movimientos, ajustes

st.set_page_config(
    page_title="Consorcio San Miguel",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS Minimalistas Oficiales
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .header-minimal {
            background-color: #0B2545;
            padding: 20px 30px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 4px solid #F57C00;
        }
        .header-title { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
        .header-user { font-size: 13px; opacity: 0.9; font-weight: 500; }
        
        div.stButton > button {
            background-color: #F57C00 !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            font-size: 15px !important;
            width: 100%;
        }
        div.stButton > button:hover { background-color: #E65100 !important; }
        
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

au.verificar_sesion()

if not st.session_state.logged_in:
    au.login_form()
    st.stop()

sh = db.conectar_sheets()
if sh is None:
    st.error("Error crítico de enlace con Google Cloud.")
    st.stop()

st.markdown(f"""
    <div class="header-minimal">
        <div class="header-title">CONSORCIO SAN MIGUEL</div>
        <div class="header-user">{st.session_state.username} — [{st.session_state.user_role}]</div>
    </div>
""", unsafe_allow_html=True)

# Menú con la nueva sección Inicio (Carátula)
opciones_menu = ["Inicio", "Dashboard", "Reporte Stock", "Movimientos", "Ajustes"]
opcion_seleccionada = st.segmented_control("Menu", options=opciones_menu, default="Inicio", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# Enrutador de módulos
if opcion_seleccionada == "Inicio":
    home.render(sh)
elif opcion_seleccionada == "Dashboard":
    dashboard.render(sh)
elif opcion_seleccionada == "Reporte Stock":
    reporte_stock.render(sh)
elif opcion_seleccionada == "Movimientos":
    movimientos.render(sh)
elif opcion_seleccionada == "Ajustes":
    ajustes.render(sh)

st.markdown("<br><hr>", unsafe_allow_html=True)
col_out1, col_out2, col_out3 = st.columns([1, 1, 1])
with col_out2:
    if st.button("Salir del Sistema", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = ""
        st.rerun()
