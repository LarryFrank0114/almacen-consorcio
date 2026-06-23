import streamlit as st
import database as db
from modulos import home, dashboard, reporte_stock, movimientos, ajustes, auditoria

# Configuración inicial de la página
st.set_page_config(
    page_title="Almacén Consorcio - Mario Edition",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =======================================================================
# 🍄 INTERFAZ PREMIUM ESTILO SUPER MARIO BROS (ALTO CONTRASTE)
# =======================================================================
st.markdown("""
    <style>
        /* Importar fuente retro pixelada */
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 1. Fondo de la App: Escena de Mario Bros optimizada para no perder lectura */
        .stApp {
            background-image: linear-gradient(rgba(20, 22, 25, 0.85), rgba(20, 22, 25, 0.85)), 
                              url('https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?q=80&w=1920');
            background-size: cover;
            background-attachment: fixed;
            color: #FFFFFF !important;
        }
        
        /* 2. Tipografía General y Textos */
        p, label, span, .stMarkdown {
            color: #F4F4F4 !important;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
        }
        
        /* Títulos Pixelados estilo Arcade (Rojo Mario y Amarillo Moneda) */
        h1, h2, h3, h4, .retro-text {
            font-family: 'Press Start 2P', cursive !important;
            line-height: 1.5;
        }
        
        h1 { color: #E52521 !important; font-size: 22px !important; text-shadow: 3px 3px #000; text-align: center; }
        h2 { color: #FBD000 !important; font-size: 18px !important; text-shadow: 2px 2px #000; }
        h3 { color: #43B047 !important; font-size: 15px !important; text-shadow: 2px 2px #000; }
        
        /* 3. Contenedor Principal en forma de Tubería Verde de hongo */
        .header-container {
            background-color: #1F2327;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
            /* Simulación de borde de tubería retro */
            border: 6px solid #43B047;
            box-shadow: inset 0 0 20px #1e5220, 0px 5px 15px rgba(0,0,0,0.6);
        }
        
        /* 4. BOTONES ESTILO BLOQUE DE LADRILLOS (BRICK BLOCKS) */
        div.stButton > button {
            background-color: #B2430A !important; /* Marrón/Naranja Ladrillo */
            color: #FFFFFF !important;
            font-family: 'Press Start 2P', cursive !important;
            font-size: 10px !important;
            border-radius: 4px !important;
            /* Textura de líneas de ladrillo mediante sombras internas */
            border: 4px solid #FCD116 !important;
            box-shadow: 3px 3px 0px #000000, 
                        inset 4px 4px 0px rgba(255,255,255,0.3), 
                        inset -4px -4px 0px rgba(0,0,0,0.4) !important;
            padding: 12px 5px !important;
            width: 100% !important;
            min-height: 58px !important;
            text-align: center !important;
            transition: transform 0.1s ease-in-out !important;
        }
        
        /* Efecto al golpear el bloque (Hover/Click) -> Se vuelve bloque amarillo con sorpresa */
        div.stButton > button:hover, div.stButton > button:focus {
            background-color: #FBD000 !important; /* Amarillo Moneda */
            color: #000000 !important;
            border-color: #FFFFFF !important;
            box-shadow: 0px 0px 15px #FBD000 !important;
            transform: translateY(-4px);
        }
        
        /* 5. Inputs estilo Bloque de Cuestión (?) */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {
            background-color: #212529 !important;
            color: #FBD000 !important;
            font-family: monospace;
            border: 3px solid #FBD000 !important;
            border-radius: 6px !important;
        }
        
        /* Tablas y Reportes dentro de bloques limpios */
        div[data-testid="stTable"], div[data-testid="stDataFrame"] {
            background-color: #1F2327 !important;
            border: 3px solid #43B047 !important;
            border-radius: 8px;
            padding: 12px;
        }
        
        /* Ajuste móvil de cuadrícula */
        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 10px !important;
            }
            div[data-testid="column"] {
                width: calc(50% - 5px) !important;
                flex-min-width: calc(50% - 5px) !important;
                margin-bottom: 5px !important;
            }
        }
    </style>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="theme-color" content="#141619">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/1407/1407123.png">

    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('data:text/javascript;base64,Z2xvYmFsVGhpcy5hZGRFdmVudExpc3RlbmVyKCdmeXRjaCcsIGV2ID0+IGV2LnJlc3BvbmRXaXRoKGZldGNoKGV2LnJlcXVlc3QpKSk7')
            .then(() => console.log('Mario Logística Active'));
        }
    </script>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 PANTALLA DE ACCESO (MUNDO 1-1)
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<br><br><h1>🍄 MARIO CORE - LOGISTICS</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #FBD000; font-size:12px;' class='retro-text'>INGRESE SUS CREDENCIALES PLAYER 1</h4>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    with col_l2:
        user_input = st.text_input("USUARIO:")
        pass_input = st.text_input("PASSWORD:", type="password")
        if st.button("START"):
            if user_input != "" and pass_input != "": 
                st.session_state.autenticado = True
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas. Intente otra vez.")
    st.stop()

# =======================================================================
# 🏢 TUBERÍA DE ENCABEZADO (POST-LOGIN)
# =======================================================================
user_activo = st.session_state.username
LISTA_ADMINS = ["larry", "supervisor", "admin", "piero pezo"] 
es_admin_o_super = user_activo.lower().strip() in LISTA_ADMINS

st.markdown(f"""
    <div class="header-container">
        <h1>MARIO LOGISTICS SYSTEM</h1>
        <div style="color:#FBD000; font-family:'Press Start 2P'; font-size:10px; margin-top:8px;">
            PLAYER: <span style="color:#FFF;">{user_activo.upper()}</span> | LEVEL 1-1
        </div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 SELECCIÓN DE PANELES (BOTONES LADRILLO)
# =======================================================================
if es_admin_o_super:
    opciones_menu = ["🏠\nINICIO", "📊\nPANEL", "📦\nSTOCK", "🔄\nKARDEX", "📋\nAUDIT", "⚙️\nSETUP"]
else:
    opciones_menu = ["🏠\nINICIO", "📊\nPANEL", "📦\nSTOCK", "📋\nAUDIT"]

cols_nav = st.columns(len(opciones_menu))

for idx, opcion in enumerate(opciones_menu):
    with cols_nav[idx]:
        nombre_tecnico_menu = opcion.split("\n")[1] if "\n" in opcion else opcion
        if st.button(opcion, use_container_width=True, key=f"btn_{nombre_tecnico_menu}"):
            if "STOCK" in nombre_tecnico_menu: st.session_state.menu_actual = "Stock Consolidados"
            elif "KARDEX" in nombre_tecnico_menu: st.session_state.menu_actual = "Movimientos (Kardex)"
            elif "AUDIT" in nombre_tecnico_menu: st.session_state.menu_actual = "Auditoría de Terreno"
            elif "SETUP" in nombre_tecnico_menu: st.session_state.menu_actual = "Ajustes del Sistema"
            elif "PANEL" in nombre_tecnico_menu: st.session_state.menu_actual = "Panel de Control"
            else: st.session_state.menu_actual = "Inicio"
            st.rerun()

st.markdown("<hr style='margin-top:5px; margin-bottom:20px; border-color:#43B047; border-width:3px;'>", unsafe_allow_html=True)

# =======================================================================
# 🔌 ENRUTADOR SEGURO DE CONEXIÓN
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

# Botón de Game Over / Salida
st.markdown("---")
if st.button("🚪 GAME OVER (LOGOUT)", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
