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
# 🎨 NUEVO TEMA CLARO CORPORATIVO (PALETA BLANCO Y CELESTE SEDAPAL)
# =======================================================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 1. Fondo general de la aplicación en Blanco Puro */
        .stApp {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
        }
        
        /* 2. Forzar que los textos globales sean legibles en fondo claro */
        h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
            color: #1E293B !important;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        /* 3. Contenedor del Título Principal */
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
        
        /* 4. Cajas informativas y alertas en tono celeste suave */
        div[data-testid="stInfoHoverColumns"], .stAlert, div[data-testid="stNotification"] {
            background-color: #F0F6FA !important;
            border-left: 5px solid #0076A8 !important;
            color: #1E293B !important;
        }
        
        /* 5. Estilización de los Botones Superiores de Navegación */
        div.stButton > button {
            background-color: #F8FAFC !important;
            color: #005492 !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 12px 20px !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            width: 100% !important;
            min-height: 58px !important;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.02) !important;
            transition: all 0.25s ease-in-out !important;
        }
        
        /* Hover de los botones superiores */
        div.stButton > button:hover {
            background-color: #0076A8 !important;
            color: #FFFFFF !important;
            border-color: #0076A8 !important;
            box-shadow: 0px 6px 12px rgba(0, 118, 168, 0.25) !important;
            transform: translateY(-2px);
        }
        
        /* Campos de texto y selectores */
        .stTextInput input, .stSelectbox div {
            background-color: #F8FAFC !important;
            color: #1E293B !important;
            border: 1px solid #CBD5E1 !important;
        }
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🏢 ENCABEZADO PRINCIPAL
# =======================================================================
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏢 CONSORCIO SAN MIGUEL</h1>
        <div class="header-subtitle">Sistema Integrado de Control Logístico y Gestión de Infraestructura Externa</div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 NAVEGACIÓN HORIZONTAL
# =======================================================================
cols_nav = st.columns(6)

with cols_nav[0]:
    if st.button("🏠\nInicio", use_container_width=True):
        st.session_state.menu_actual = "Inicio"
        st.rerun()

with cols_nav[1]:
    if st.button("📊\nPanel Control", use_container_width=True):
        st.session_state.menu_actual = "Panel de Control"
        st.rerun()

with cols_nav[2]:
    if st.button("📦\nStock Consolidados", use_container_width=True):
        st.session_state.menu_actual = "Stock Consolidados"
        st.rerun()

with cols_nav[3]:
    if st.button("🔄\nMovimientos", use_container_width=True):
        st.session_state.menu_actual = "Movimientos (Kardex)"
        st.rerun()

with cols_nav[4]:
    if st.button("📋\nAuditoría Terreno", use_container_width=True):
        st.session_state.menu_actual = "Auditoría de Terreno"
        st.rerun()

with cols_nav[5]:
    if st.button("⚙️\nAjustes", use_container_width=True):
        st.session_state.menu_actual = "Ajustes del Sistema"
        st.rerun()

st.markdown("<hr style='margin-top:5px; margin-bottom:20px; border-color:#E2E8F0;'>", unsafe_allow_html=True)

# =======================================================================
# 🔌 ENRUTADOR DINÁMICO
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
