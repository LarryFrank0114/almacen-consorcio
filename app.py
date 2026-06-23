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
# 🌐 SISTEMA DE IDIOMAS MULTILENGUAJE CON ICONO DE HONGO (🍄)
# =======================================================================
if "lang" not in st.session_state:
    st.session_state.lang = "Español 🇪🇸"

TRADUCCIONES = {
    "Español 🇪🇸": {
        "titulo_login": "🍄 CONSORCIO SAN MIGUEL - LOGISTIC",
        "sub_login": "INGRESE SUS CREDENCIALES PLAYER 1",
        "usuario": "USUARIO:",
        "password": "PASSWORD:",
        "error_login": "❌ Credenciales incorrectas.",
        "player": "PLAYER",
        "escenario": "ESCENARIO",
        "titulo_graficos": "### ⚙️ Configuración Gráfica del Nivel",
        "select_mundo": "Selecciona el Escenario (Mundo):",
        "nivel_sombra": "Nivel de Sombra del Fondo (%):",
        "help_sombra": "Baja el porcentaje para que el cielo de Mario se vea más brillante y nítido.",
        "btn_inicio": "🍄\nINICIO",
        "btn_panel": "🍄\nPANEL",
        "btn_stock": "🍄\nSTOCK",
        "btn_kardex": "🍄\nKARDEX",
        "btn_audit": "🍄\nAUDIT",
        "btn_setup": "🍄\nSETUP",
        "logout": "🚪 GAME OVER (LOGOUT)"
    },
    "中文 🇨🇳": {
        "titulo_login": "🍄 聖米格爾聯盟 - 物流管理系统",
        "sub_login": "请输入玩家 1 的凭证 (PLAYER 1 CREDENTIALS)",
        "usuario": "用户名 (USER):",
        "password": "密码 (PASSWORD):",
        "error_login": "❌ 凭证错误，请重试。",
        "player": "玩家 (PLAYER)",
        "escenario": "游戏场景 (WORLD)",
        "titulo_graficos": "### ⚙️ 级别图形显示设置",
        "select_mundo": "选择游戏背景 (MUNDO):",
        "nivel_sombra": "背景阴影暗度 (%):",
        "help_sombra": "降低百分比可让马里奥的天空背景更亮、更清晰。",
        "btn_inicio": "🍄\n主页 (HOME)",
        "btn_panel": "🍄\n仪表盘 (DASHBOARD)",
        "btn_stock": "🍄\n库存 (STOCK)",
        "btn_kardex": "🍄\n流水 (KARDEX)",
        "btn_audit": "🍄\n审计 (AUDIT)",
        "btn_setup": "🍄\n设置 (SETUP)",
        "logout": "🚪 游戏结束 (注销登录)"
    },
    "English 🇬🇧": {
        "titulo_login": "🍄 CONSORCIO SAN MIGUEL - LOGISTICS",
        "sub_login": "ENTER YOUR CREDENTIALS PLAYER 1",
        "usuario": "USERNAME:",
        "password": "PASSWORD:",
        "error_login": "❌ Incorrect credentials.",
        "player": "PLAYER",
        "escenario": "STAGE",
        "titulo_graficos": "### ⚙️ Level Graphics Configuration",
        "select_mundo": "Select Stage (World):",
        "nivel_sombra": "Background Shadow Level (%):",
        "help_sombra": "Lower the percentage to make Mario's sky brighter and clearer.",
        "btn_inicio": "🍄\nHOME",
        "btn_panel": "🍄\nPANEL",
        "btn_stock": "🍄\nSTOCK",
        "btn_kardex": "🍄\nKARDEX",
        "btn_audit": "🍄\nAUDIT",
        "btn_setup": "🍄\nSETUP",
        "logout": "🚪 GAME OVER (LOGOUT)"
    }
}

t = TRADUCCIONES[st.session_state.lang]

if "mario_world" not in st.session_state:
    st.session_state.mario_world = "Fondo clasico"

if "filtro_oscuro" not in st.session_state:
    st.session_state.filtro_oscuro = 50

# Enlaces de imágenes de tu repositorio GitHub[cite: 1]
FONDOS_MUNDO = {
    "Fondo clasico": "https://github.com/LarryFrank0114/almacen-consorcio/blob/main/imagenes/fondo-retro-mario2.jpg?raw=true",
    "Fondo Verde": "https://github.com/LarryFrank0114/almacen-consorcio/blob/main/imagenes/mario-bross-fondo.jpg?raw=true",
    "Fondo 3D": "https://github.com/LarryFrank0114/almacen-consorcio/blob/main/imagenes/mario-bross-fondo-3d.jpg?raw=true"
}

url_fondo_actual = FONDOS_MUNDO.get(st.session_state.mario_world, "")
alfa_css = st.session_state.filtro_oscuro / 100.0

# Styles de Super Mario con mejoras en selectores
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
        .stApp {{
            background-color: #5c94fc; 
            background-image: linear-gradient(rgba(16, 18, 22, {alfa_css}), rgba(16, 18, 22, {alfa_css + 0.1 if alfa_css <= 0.9 else 1.0})), url('{url_fondo_actual}');
            background-size: cover; background-attachment: fixed; background-position: center bottom; color: #FFFFFF !important;
        }}
        p, label, span, .stMarkdown {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}
        h1, h2, h3, h4, .retro-text {{ font-family: 'Press Start 2P', cursive !important; line-height: 1.5; }}
        h1 {{ color: #E52521 !important; font-size: 22px !important; text-shadow: 3px 3px #000; text-align: center; }}
        h2 {{ color: #FBD000 !important; font-size: 18px !important; text-shadow: 2px 2px #000; }}
        h3 {{ color: #43B047 !important; font-size: 15px !important; text-shadow: 2px 2px #000; }}
        .header-container {{ background-color: rgba(31, 35, 39, 0.9); padding: 24px; border-radius: 12px; margin-bottom: 25px; text-align: center; border: 6px solid #43B047; box-shadow: inset 0 0 20px #1e5220, 0px 5px 15px rgba(0,0,0,0.6); }}
        div.stButton > button {{
            background-color: #B2430A !important; color: #FFFFFF !important; font-family: 'Press Start 2P', cursive !important; font-size: 10px !important;
            border-radius: 4px !important; border: 4px solid #FCD116 !important; box-shadow: 3px 3px 0px #000000, inset 4px 4px 0px rgba(255,255,255,0.3) !important;
            padding: 12px 5px !important; width: 100% !important; min-height: 58px !important; transition: transform 0.1s ease-in-out !important;
        }}
        div.stButton > button:hover {{ background-color: #FBD000 !important; color: #000000 !important; border-color: #FFFFFF !important; transform: translateY(-4px); }}
        .stSelectbox div[data-baseweb="select"] {{ background-color: rgba(31, 35, 39, 0.9) !important; border: 3px solid #FBD000 !important; border-radius: 6px !important; }}
        .stSelectbox div[data-baseweb="select"] * {{ color: #FBD000 !important; font-family: monospace !important; font-weight: bold !important; }}
        .stTextInput input, .stTextArea textarea {{ background-color: rgba(31, 35, 39, 0.9) !important; color: #FBD000 !important; border: 3px solid #FBD000 !important; }}
        div[data-testid="stTable"], div[data-testid="stDataFrame"] {{ background-color: rgba(31, 35, 39, 0.9) !important; border: 3px solid #43B047 !important; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# =======================================================================
# 🔐 PANTALLA DE ACCESO (LOGIN)
# =======================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col_lang1, col_lang2 = st.columns([2.5, 1])
    with col_lang2:
        lang_login = st.selectbox("🌐 LANGUAGE / 语言:", list(TRADUCCIONES.keys()), key="lang_selector_login")
        if lang_login != st.session_state.lang:
            st.session_state.lang = lang_login
            st.rerun()

    st.markdown(f"<br><h1>{t['titulo_login']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #FBD000; font-size:12px;' class='retro-text'>{t['sub_login']}</h4>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    with col_l2:
        user_input = st.text_input(t["usuario"])
        pass_input = st.text_input(t["password"], type="password")
        if st.button("START"):
            if user_input.strip() != "" and pass_input != "": 
                st.session_state.autenticado = True
                st.session_state.username = user_input.strip()
                st.rerun()
            else:
                st.error(t["error_login"])
    st.stop()

# =======================================================================
# 🏢 ASIGNACIÓN DE IDENTIDAD Y ROLES DE OPERACIÓN
# =======================================================================
user_raw = st.session_state.username.lower()

# Jerarquía Estricta de Cargos y Títulos de Visualización
if user_raw == "larry":
    display_name = "Larry Rodriguez"
    display_cargo = "Jefe de Almacenes Externos"
    es_admin_total = True
    es_modo_lectura = False
elif user_raw in ["supervisor", "gerencia china", "gerencia", "auditor"]:
    display_name = st.session_state.username.upper()
    display_cargo = "Supervisor / Control de Auditoría G-China"
    es_admin_total = False
    es_modo_lectura = True  # Bloqueado en Modo Lectura total
else:
    # Responsables de Almacén autorizados
    mapeo_responsables = {
        "piero pezo": "Piero Pezo (Responsable Almacén 10)",
        "gregorio rodriguez": "Gregorio Rodriguez (Responsable Almacén 01)",
        "marcial huayta": "Marcial Huayta (Responsable Almacén 08)",
        "enrique sanchez": "Enrique Sanchez (Responsable Almacén 06)"
    }
    display_name = mapeo_responsables.get(user_raw, st.session_state.username.upper())
    display_cargo = "Responsable de Almacén Autorizado"
    es_admin_total = False
    es_modo_lectura = False

# Encabezado Principal de Información Estilizado
st.markdown(f"""
    <div class="header-container">
        <h1>CMEC 2 - CONSORCIO SAN MIGUEL LOGISTICS SYSTEM</h1>
        <h2>RUC 20607900052</h2>
        <div style="color:#FBD000; font-family:'Press Start 2P'; font-size:9px; margin-top:8px; line-height: 1.8;">
            {t['player']}: <span style="color:#FFF;">{display_name}</span><br>
            CARGO: <span style="color:#43B047;">{display_cargo}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if "menu_actual" not in st.session_state:
    st.session_state.menu_actual = "Inicio"

# =======================================================================
# 🧭 NAVEGACIÓN DINÁMICA TRADUCIDA
# =======================================================================
# Todos los usuarios ven el Kardex, pero su rol interno condiciona qué hacen dentro
if es_admin_total:
    opciones_menu = [t["btn_inicio"], t["btn_panel"], t["btn_stock"], t["btn_kardex"], t["btn_audit"], t["btn_setup"]]
else:
    opciones_menu = [t["btn_inicio"], t["btn_panel"], t["btn_stock"], t["btn_kardex"], t["btn_audit"]]

cols_nav = st.columns(len(opciones_menu))

for idx, opcion in enumerate(opciones_menu):
    with cols_nav[idx]:
        nombre_tecnico_menu = opcion.split("\n")[1] if "\n" in opcion else opcion
        if st.button(opcion, use_container_width=True, key=f"btn_{idx}"):
            if "STOCK" in nombre_tecnico_menu or "库存" in nombre_tecnico_menu: st.session_state.menu_actual = "Stock Consolidados"
            elif "KARDEX" in nombre_tecnico_menu or "流水" in nombre_tecnico_menu: st.session_state.menu_actual = "Movimientos (Kardex)"
            elif "AUDIT" in nombre_tecnico_menu or "审计" in nombre_tecnico_menu: st.session_state.menu_actual = "Auditoría de Terreno"
            elif "SETUP" in nombre_tecnico_menu or "设置" in nombre_tecnico_menu: st.session_state.menu_actual = "Ajustes del Sistema"
            elif "PANEL" in nombre_tecnico_menu or "仪表盘" in nombre_tecnico_menu: st.session_state.menu_actual = "Panel de Control"
            else: st.session_state.menu_actual = "Inicio"
            st.rerun()

st.markdown("<hr style='margin-top:5px; margin-bottom:20px; border-color:#43B047; border-width:3px;'>", unsafe_allow_html=True)

# =======================================================================
# 🔌 ENRUTADOR DE SECCIONES CON CONTROL DE ACCESO
# =======================================================================
sh = db.conectar_sheets()

if st.session_state.autenticado:
    if st.session_state.menu_actual == "Ajustes del Sistema":
        if es_admin_total:
            ajustes.render(sh)
            st.markdown("<br>---", unsafe_allow_html=True)
            st.markdown(t["titulo_graficos"])
            c1, c2, c3 = st.columns(3)
            with c1:
                nuevo_fondo = st.selectbox(t["select_mundo"], list(FONDOS_MUNDO.keys()), key="mario_world_selector")
                if nuevo_fondo != st.session_state.mario_world:
                    st.session_state.mario_world = nuevo_fondo
                    st.rerun()
            with c2:
                nueva_oscuridad = st.slider(t["nivel_sombra"], min_value=10, max_value=90, value=st.session_state.filtro_oscuro, step=5)
                if nueva_oscuridad != st.session_state.filtro_oscuro:
                    st.session_state.filtro_oscuro = nueva_oscuridad
                    st.rerun()
            with c3:
                lang_global = st.selectbox("🌐 IDIOMA:", list(TRADUCCIONES.keys()), key="lang_selector_global", index=list(TRADUCCIONES.keys()).index(st.session_state.lang))
                if lang_global != st.session_state.lang:
                    st.session_state.lang = lang_global
                    st.rerun()
        else:
            st.error("🚫 ACCESO DENEGADO. Solo el Jefe de Almacenes Externos (Larry Rodriguez) puede modificar la configuración estructural.")
            
    elif st.session_state.menu_actual == "Inicio":
        try: home.render(sh)
        except TypeError: home.render()
        
    elif st.session_state.menu_actual == "Panel de Control": 
        dashboard.render(sh)
        
    elif st.session_state.menu_actual == "Stock Consolidados": 
        reporte_stock.render(sh)
        
    elif st.session_state.menu_actual == "Movimientos (Kardex)":
        # Ejecución del módulo Kardex pasando las banderas precisas de identidad y rol de lectura
        movimientos.render(sh, usuario=st.session_state.username, modo_lectura=es_modo_lectura)
                
    elif st.session_state.menu_actual == "Auditoría de Terreno": 
        auditoria.render(sh)

# Botón de Salida Traducido
st.markdown("---")
if st.button(t["logout"], use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.username = None
    st.session_state.menu_actual = "Inicio"
    st.rerun()
