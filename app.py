import streamlit as st
import pandas as pd
from datetime import datetime
import database as db  # Conexión con nuestro módulo de Google Sheets

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y SESIÓN
# ==========================================
st.set_page_config(
    page_title="Sistema de Gestión de Almacenes - Consorcio San Miguel",
    page_icon="📦",
    layout="wide"
)

# Inicializar estados de sesión para control de login
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None
if "rol_actual" not in st.session_state:
    st.session_state.rol_actual = None

# Cargar catálogo maestro temporal si no existe en sesión (Módulo 4)
if "maestro_materiales" not in st.session_state:
    st.session_state.maestro_materiales = pd.DataFrame([
        {"Código": "HID-PO-01", "Material": "Tubo Polietileno 110mm Pn10", "Unidad": "Metros"},
        {"Código": "ACC-CR-05", "Material": "Cruceta de Hierro Fundido DN 100", "Unidad": "Unidades"},
        {"Código": "VAL-CO-02", "Material": "Válvula de Compuerta C/Brida 4\"", "Unidad": "Unidades"}
    ])

# Conectar a la base de datos de Google Sheets
sh = db.conectar_sheets()

if sh is None:
    st.error("❌ No se pudo establecer la comunicación con el servidor central de Google Sheets. Verifique la configuración de Secrets.")
    st.stop()

# ==========================================
# PANTALLA DE CONTROL DE ACCESO (LOGIN)
# ==========================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🔐 CONTROL DE ACCESO LOGÍSTICO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Megaproyecto Sectorial Saneamiento 'Nueva Rinconada'</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("formulario_login"):
            usuario = st.text_input("Usuario")
            contrasena = st.text_input("Contraseña", type="password")
            btn_ingresar = st.form_submit_button("Iniciar Sesión")
            
            if btn_ingresar:
                # Validación simple integrada de usuarios del consorcio
                if usuario.lower() == "larry" and contrasena == "admin123":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Larry Frank Rodriguez"
                    st.session_state.rol_actual = "Jefe de Almacenes"
                    st.rerun()
                elif usuario.lower() == "supervisor" and contrasena == "obra2026":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Ing. Carlos Mendoza"
                    st.session_state.rol_actual = "Supervisor de Obra"
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Intente nuevamente.")
    st.stop()

# ==========================================
# ESTRUCTURA PRINCIPAL (SIDEBAR - MENÚ)
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.usuario_actual}")
    st.markdown(f"**Rol:** {st.session_state.rol_actual}")
    st.markdown("<span style='color:green;'>● Conectado a Google Sheets</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📌 MENÚ DE OPERACIONES")
    opcion_menu = st.radio(
        "Seleccione un módulo:",
        [
            "📊 Dashboard Gerencial",
            "📖 Reporte de Stock Actual",
            "🔄 Registrar Movimiento (Guías/Vales)",
            "⚙️ Configurar Almacenes (1, 6, 8, 10)"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 Salir del Sistema"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.session_state.rol_actual = None
        st.rerun()

# ==========================================
# MÓDULO 1: DASHBOARD GERENCIAL
# ==========================================
if opcion_menu == "📊 Dashboard Gerencial":
    st.markdown("# 📊 DASHBOARD CORPORATIVO DE MOVIMIENTOS")
    st.markdown("---")
    
    # Intentar leer el historial transaccional de Google Sheets
    try:
        ws_historial = sh.worksheet("historial")
        df_historial = pd.DataFrame(ws_historial.get_all_records())
    except Exception:
        df_historial = pd.DataFrame()
        
    if df_historial.empty:
        st.info("No se registran movimientos transaccionales en el historial para generar gráficos.")
    else:
        # Generación de indicadores clave de rendimiento (KPIs)
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.metric("Total Transacciones", len(df_historial))
        with col_kpi2:
            ingresos = len(df_historial[df_historial['Tipo'] == 'INGRESO'])
            st.metric("Total Ingresos (Guías)", ingresos)
        with col_kpi3:
