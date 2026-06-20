import streamlit as st
import database as db
from modulos import home, dashboard, reporte_stock, movimientos, ajustes, auditoria

# Configuración inicial de la página (¡Debe ser la primera línea!)
st.set_page_config(
    page_title="Consorcio San Miguel - Gestión de Almacenes",
    layout="wide",
    initial_sidebar_state="collapsed" # Mantiene la barra lateral cerrada por defecto
)

# =======================================================================
# 🎨 ESTILOS PERSONALIZADOS - PALETA SEDAPAL (Azul Corporativo y Blanco)
# =======================================================================
st.markdown("""
    <style>
        /* Ocultar decoración por defecto de Streamlit arriba */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Contenedor principal del encabezado */
        .header-container {
            background-color: #005492;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        .header-title {
            color: white !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
            margin: 0;
            padding: 0;
            font-size: 28px;
            letter-spacing: 0.5px;
        }
        .header-subtitle {
            color: #E3F2FD !important;
            font-size: 14px;
            margin-top: 5px;
            opacity: 0.9;
        }
        
        /* Estilización de los botones de navegación superiores */
        div.stButton > button {
            background-color: #ffffff !important;
            color: #005492 !important;
            border: 2px solid #005492 !important;
            border-radius: 8px !important;
            padding: 12px 20px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            width: 100% !important;
            min-height: 55px !important;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease-in-out !important;
        }
        
        /* Efecto al pasar el mouse por encima (Hover) */
        div.stButton > button:hover {
            background-color: #0076A8 !important;
            color: white !important;
            border-color: #0076A8 !important;
            box-shadow: 0px 5px 15px rgba(0, 118, 168, 0.3) !important;
            transform: translateY(-2px);
        }
        
        /* Estilo para el botón del módulo actualmente SELECCIONADO */
        div.stButton > button:focus, div.stButton > button[aria-selected="true"] {
            background-color: #005492 !important;
            color: white !important;
            border-color: #002D54 !important;
        }
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🏢 ENCABEZADO PRINCIPAL DE LA APLICACIÓN
# =======================================================================
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏢 CONSORCIO SAN MIGUEL</h1>
        <div class="header-subtitle">Sistema Integrado de Control Logístico y Gestión de Infraestructura Externa</div>
    </div>
""", unsafe_allow_html=True)

# Inicializar la variable de estado del menú si no existe
if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 BARRA DE NAVEGACIÓN HORIZONTAL EN EL ENCABEZADO
# =======================================================================
# Creamos 6 columnas exactas para distribuir los botones simétricamente de forma horizontal
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

st.markdown("---") # Línea divisoria elegante bajo la botonera

# =======================================================================
# 🔌 ENRUTADOR DINÁMICO DE PÁGINAS
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
