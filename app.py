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
# 🌐 SISTEMA DE CAMBIO DE MUNDOS (FONDOS DINÁMICOS)
# =======================================================================
# Inicializamos el fondo predeterminado con la estética de cielo azul (image_b9c085.png)
if "mario_world" not in st.session_state:
    st.session_state.mario_world = "Cielo Azul (Mundo 1-1)"

# Diccionario de fondos de pantalla disponibles
FONDOS_MUNDO = {
    "Cielo Azul (Mundo 1-1)": "<a href="https://es.vecteezy.com/arte-vectorial/20323090-8-poco-retro-juego-antecedentes">8-poco-retro-juego-antecedentes Vectores por Vecteezy</a>", # Clon exacto de image_b9c085.png
    "Subterráneo (Mundo 1-2)": "https://i.imgur.com/KscY9b9.png", 
    "Castillo de Bowser": "https://i.imgur.com/mS26f8U.png"
}

url_fondo_actual = FONDOS_MUNDO.get(st.session_state.mario_world, FONDOS_MUNDO["Cielo Azul (Mundo 1-1)"])

# =======================================================================
# 🍄 ESTILOS CSS AVANZADOS INTERFAZ SUPER MARIO
# =======================================================================
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Fondo dinámico basado en la selección del usuario */
        .stApp {{
            background-image: linear-gradient(rgba(16, 18, 22, 0.78), rgba(16, 18, 22, 0.85)), 
                              url('{url_fondo_actual}');
            background-size: cover;
            background-attachment: fixed;
            background-position: center bottom;
            color: #FFFFFF !important;
        }}
        
        /* Textos legibles sobre el cielo */
        p, label, span, .stMarkdown {{
            color: #F4F4F4 !important;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
            font-weight: 500;
        }}
        
        /* Encabezados pixelados */
        h1, h2, h3, h4, .retro-text {{
            font-family: 'Press Start 2P', cursive !important;
            line-height: 1.5;
        }}
        
        h1 {{ color: #E52521 !important; font-size: 22px !important; text-shadow: 3px 3px #000; text-align: center; }}
        h2 {{ color: #FBD000 !important; font-size: 18px !important; text-shadow: 2px 2px #000; }}
        h3 {{ color: #43B047 !important; font-size: 15px !important; text-shadow: 2px 2px #000; }}
        
        /* Tubería Verde como Contenedor Principal */
        .header-container {{
            background-color: #1F2327;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
            border: 6px solid #43B047;
            box-shadow: inset 0 0 20px #1e5220, 0px 5px 15px rgba(0,0,0,0.6);
        }}
        
        /* Botones estilo Bloque de Ladrillo */
        div.stButton > button {{
            background-color: #B2430A !important;
            color: #FFFFFF !important;
            font-family: 'Press Start 2P', cursive !important;
            font-size: 10px !important;
            border-radius: 4px !important;
            border: 4px solid #FCD116 !important;
            box-shadow: 3px 3px 0px #000000, 
                        inset 4px 4px 0px rgba(255,255,255,0.3), 
                        inset -4px -4px 0px rgba(0,0,0,0.4) !important;
            padding: 12px 5px !important;
            width: 100% !important;
            min-height: 58px !important;
            transition: transform 0.1s ease-in-out !important;
        }}
        
        /* Hover a Bloque de Ítem Dorado */
        div.stButton > button:hover, div.stButton > button:focus {{
            background-color: #FBD000 !important;
            color: #000000 !important;
            border-color: #FFFFFF !important;
            box-shadow: 0px 0px 15px #FBD000 !important;
            transform: translateY(-4px);
        }}
        
        /* Inputs */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{
            background-color: #1F2327 !important;
            color: #FBD000 !important;
            font-family: monospace;
            border: 3px solid #FBD000 !important;
        }}
        
        div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
            background-color: #1F2327 !important;
            border: 3px solid #43B047 !important;
            border-radius: 8px;
        }}
        
        @media (max-width: 768px) {{
            div[data-testid="stHorizontalBlock"] {{
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 10px !important;
            }}
            div[data-testid="column"] {{
                width: calc(50% - 5px) !important;
                flex-min-width: calc(50% - 5px) !important;
                margin-bottom: 5px !important;
            }}
        }}
    </style>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/1407/1407123.png">
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 PANTALLA DE ACCESO
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
                st.error("❌ Credenciales incorrectas.")
    st.stop()

# =======================================================================
# 🏢 ENCABEZADO PRINCIPAL (TUBERÍA VERDE)
# =======================================================================
user_activo = st.session_state.username
LISTA_ADMINS = ["larry", "supervisor", "admin", "piero pezo"] 
es_admin_o_super = user_activo.lower().strip() in LISTA_ADMINS

st.markdown(f"""
    <div class="header-container">
        <h1>MARIO LOGISTICS SYSTEM</h1>
        <div style="color:#FBD000; font-family:'Press Start 2P'; font-size:10px; margin-top:8px;">
            PLAYER: <span style="color:#FFF;">{user_activo.upper()}</span> | ESCENARIO: <span style="color:#43B047;">{st.session_state.mario_world.upper()}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 NAVEGACIÓN (BLOQUES DE LADRILLO)
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
# 🔌 ENRUTADOR DE SECCIONES + SELECTOR DE FONDOS EN SETUP
# =======================================================================
sh = db.conectar_sheets()

if st.session_state.autenticado:
    if st.session_state.menu_actual == "Ajustes del Sistema":
        # Renderizamos el módulo original de ajustes
        ajustes.render(sh)
        
        # 🎨 INYECTAMOS EL SELECTOR DE FONDOS DIRECTAMENTE ABAJO EN LA PESTAÑA SETUP
        st.markdown("<br>---", unsafe_allow_html=True)
        st.markdown("### 🖼️ Selector de Escenarios Logísticos")
        nuevo_fondo = st.selectbox(
            "Cambia el fondo del videojuego para toda la app:",
            list(FONDOS_MUNDO.keys()),
            index=list(FONDOS_MUNDO.keys()).index(st.session_state.mario_world)
        )
        if nuevo_fondo != st.session_state.mario_world:
            st.session_state.mario_world = nuevo_fondo
            st.rerun()
            
    elif st.session_state.menu_actual == "Inicio":
        try: home.render(sh)
        except TypeError: home.render()
    elif st.session_state.menu_actual == "Panel de Control": dashboard.render(sh)
    elif st.session_state.menu_actual == "Stock Consolidados": reporte_stock.render(sh)
    elif st.session_state.menu_actual == "Movimientos (Kardex)": movimientos.render(sh)
    elif st.session_state.menu_actual == "Auditoría de Terreno": auditoria.render(sh)  

# Botón de Salida
st.markdown("---")
if st.button("🚪 GAME OVER (LOGOUT)", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
