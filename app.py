import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURACIÓN DE LA PÁGINA (Título e Icono en la pestaña del navegador)
st.set_page_config(
    page_title="Consorcio San Miguel - Gestión de Almacenes Externos",
    page_icon="🏗️",
    layout="wide"
)

# Estilos CSS personalizados para mejorar la estética (Colores institucionales)
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1E3A8A; text-align:center; margin-bottom:5px; }
    .subtitle { font-size:18px; color:#4B5563; text-align:center; margin-bottom:25px; }
    .metric-box { background-color:#F3F4F6; padding:15px; border-radius:10px; border-left:5px solid #1D4ED8; }
    </style>
""", unsafe_allow_html=True)

# 2. BASE DE DATOS SIMULADA (En el futuro se conecta a un archivo o servidor web)
if 'inventario' not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"Código": "TUB-PE-110", "Material": "Tubería PEAD 110mm (Saneamiento)", "Almacén": "Almacén 6", "Ubicación": "Estante A - Nivel 2", "Stock": 140, "Unidad": "Metros"},
        {"Código": "VAL-CO-04", "Material": "Válvula de Compuerta 4''", "Almacén": "Almacén 8", "Ubicación": "Pallet 12", "Stock": 25, "Unidad": "Unidades"},
        {"Código": "ACC-TEE-110", "Material": "Accesorio Tee Inyectada 110mm", "Almacén": "Almacén 10", "Ubicación": "Caja 05", "Stock": 8, "Unidad": "Unidades"},
        {"Código": "HID-PO-02", "Material": "Hidrante de Poste Completo", "Almacén": "Almacén 6", "Ubicación": "Zona Patio B", "Stock": 15, "Unidad": "Unidades"}
    ])

# 3. CONTROL DE ACCESO / AUTENTICACIÓN (LOGIN SENCILLO)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

def login():
    st.markdown("<div class='main-title'>PLATAFORMA WEB INTEGRAL DE GESTIÓN LOGÍSTICA</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Megaproyecto Sectorial Saneamiento \"Nueva Rinconada\" - SEDAPAL</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.info("💡 **Credenciales de prueba para clase:**\n- Admin (Tú): `larry` / `admin123`\n- Supervisor (Jefe/SEDAPAL): `supervisor` / `super123`")
        with st.form("Formulario de Login"):
            st.markdown("### 🔐 Ingreso al Sistema")
            usuario = st.text_input("Usuario")
            contraseña = st.text_input("Contraseña", type="password")
            boton_ingresar = st.form_submit_button("Iniciar Sesión")
            
            if boton_ingresar:
                if usuario == "larry" and contraseña == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.session_state.username = "Larry (Jefe de Almacenes)"
                    st.rerun()
                elif usuario == "supervisor" and contraseña == "super123":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Supervisor"
                    st.session_state.username = "Ing. de Guardia SEDAPAL"
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

# 4. ENTORNO PRINCIPAL DE LA APLICACIÓN (Si el Login es exitoso)
if not st.session_state.logged_in:
    login()
else:
    # BARRA LATERAL (Sidebar) Corporativa
    with st.sidebar:
        st.markdown(f"### 👤 Bienvenido,\n**{st.session_state.username}**")
        st.caption(f"Rol: {st.session_state.user_role}")
        st.markdown("---")
        
        # Simulación de carga de logo institucional mediante texto estilizado o URL
        st.markdown("<h3 style='color:#1D4ED8;'>CONSORCIO SAN MIGUEL</h3>", unsafe_allow_html=True)
        st.caption("RUC: 20607900052")
        
        st.markdown("---")
        opcion_menu = st.radio(
            "📌 MENÚ DE NAVEGACIÓN",
            ["📊 Dashboard y Stock en Vivo", "🔄 Operaciones (Vales y Guías)", "📍 Ubicación de Almacenes"]
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.rerun()

    # --- PESTAÑA 1: DASHBOARD Y STOCK EN VIVO ---
    if opcion_menu == "📊 Dashboard y Stock en Vivo":
        st.markdown("<div class='main-title'>📊 CONTROL DE STOCK EN TIEMPO REAL</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Tarjetas de resumen (KPIs rápidos)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("<div class='metric-box'><b>Almacenes Activos</b><br><span style='font-size:24px; font-weight:bold;'>3 (Sedes 6, 8, 10)</span></div>", unsafe_allow_html=True)
        with c2:
            items_total = len(st.session_state.inventario)
            st.markdown(f"<div class='metric-box'><b>Ítems Registrados</b><br><span style='font-size:24px; font-weight:bold;'>{items_total} materiales</span></div>", unsafe_allow_html=True)
        with c3:
            alertas = len(st.session_state.inventario[st.session_state.inventario['Stock'] <= 10])
            st.markdown(f"<div class='metric-box' style='border-left:5px solid #EF4444;'><b>Alertas de Stock Crítico</b><br><span style='font-size:24px; font-weight:bold; color:#EF4444;'>{alertas} Ítems</span></div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='metric-box' style='border-left:5px solid #10B981;'><b>Estado del Servidor</b><br><span style='font-size:24px; font-weight:bold; color:#10B981;'>En Línea Cloud</span></div>", unsafe_allow_html=True)
            
        st.markdown("### 📋 Buscador Inteligente de Materiales")
        buscar = st.text_input("🔍 Ingresa el nombre del material o código para buscar en las 3 sedes:")
        
        df_filtrado = st.session_state.inventario
        if buscar:
            df_filtrado = df_filtrado[df_filtrado['Material'].str.contains(buscar, case=False) | df_filtrado['Código'].str.contains(buscar, case=False)]
            
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # --- PESTAÑA 2: OPERACIONES (REGISTROS SEGÚN EL ROL) ---
    elif opcion_menu == "🔄 Operaciones (Vales y Guías)":
        st.markdown("<div class='main-title'>🔄 REGISTRO DE MOVIMIENTOS LOGÍSTICOS</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # SEGURIDAD: Validamos si el usuario tiene permiso para modificar datos
        if st.session_state.user_role != "Administrador":
            st.warning(f"🔒 **Acceso Restringido:** Su usuario con rol de **{st.session_state.user_role}** solo tiene permisos de lectura. No puede ingresar vales ni guías.")
        else:
            st.success("🔓 **Acceso Concedido:** Modo Operario/Jefe habilitado para actualizaciones de stock.")
            
            tipo_op = st.selectbox("Seleccione el tipo de operación:", ["Ingreso por Guía de Remisión", "Egreso por Vale de Consumo", "Devolución (Vale de Ingreso)"])
            
            with st.form("Formulario Operativo"):
                st.markdown(f"### {tipo_op}")
                doc_ref = st.text_input("Número de Documento (Ej: GR-001-9843 o V-652)")
                proveedor_obra = st.text_input("Proveedor o Frente de Obra Destino (SJM, VMT, VES)")
                
                material_sel = st.selectbox("Material involucrado:", st.session_state.inventario['Material'].tolist())
                almacen_sel = st.selectbox("Almacén de Destino/Origen:", ["Almacén 6", "Almacén 8", "Almacén 10"])
                cantidad_op = st.number_input("Cantidad", min_value=1, step=1)
                
                btn_procesar = st.form_submit_button("💾 Procesar y Actualizar Inventario en Vivo")
                
                if btn_procesar:
                    # Lógica matemática básica para modificar el DataFrame en caliente
                    idx = st.session_state.inventario[st.session_state.inventario['Material'] == material_sel].index[0]
                    stock_actual = st.session_state.inventario.at[idx, 'Stock']
                    
                    if "Egreso" in tipo_op:
                        if stock_actual >= cantidad_op:
                            st.session_state.inventario.at[idx, 'Stock'] = stock_actual - cantidad_op
                            st.success(f"✔️ Egreso registrado. Stock actualizado de {material_sel}. Nuevo stock: {stock_actual - cantidad_op}")
                        else:
                            st.error("❌ Stock Insuficiente en el almacén para realizar este egreso.")
                    else:
                        st.session_state.inventario.at[idx, 'Stock'] = stock_actual + cantidad_op
                        st.success(f"✔️ Ingreso registrado con éxito. Nuevo stock: {stock_actual + cantidad_op}")

    # --- PESTAÑA 3: UBICACIÓN DE ALMACENES EXTERNOS ---
    elif opcion_menu == "📍 Ubicación de Almacenes":
        st.markdown("<div class='main-title'>📍 RED DE ALMACENES EXTERNOS (PROYECTO NUEVA RINCONADA)</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### 🧑‍💼 Directorio de Personal y Encargados")
        
        # Tabla informativa de encargados
        tabla_encargados = pd.DataFrame([
            {"Sede": "Almacén 6", "Distrito": "San Juan de Miraflores (SJM)", "Encargado de Sede": "Técnico Logístico Juan Carlos R.", "Contacto": "994-XXX-XXX", "Especialidad": "Tuberías Pesadas y Conexiones PEAD"},
            {"Sede": "Almacén 8", "Distrito": "Villa María del Triunfo (VMT)", "Encargado de Sede": "Ing. Soporte Operativo Carlos M.", "Contacto": "981-XXX-XXX", "Especialidad": "Válvulas y Componentes de Presión"},
            {"Sede": "Almacén 10", "Distrito": "Villa El Salvador (VES)", "Encargado de Sede": "Supervisor de Campo Luis A.", "Contacto": "955-XXX-XXX", "Especialidad": "Accesorios Menores, Pernos e Hidrantes"}
        ])
        st.table(tabla_encargados)
        
        st.markdown("### 🗺️ Geolocalización en Vivo")
        st.write("A continuación se muestra la localización de las sedes externas en los distritos del área de influencia del proyecto:")
        
        # Coordenadas aproximadas de SJM, VMT y VES en Lima para el mapa interactivo de Streamlit
        map_data = pd.DataFrame({
            'lat': [-12.1644, -12.1702, -12.2111],
            'lon': [-76.9622, -76.9385, -76.9344],
            'Almacén': ['Almacén 6 (SJM)', 'Almacén 8 (VMT)', 'Almacén 10 (VES)']
        })
        st.map(map_data)
        
        # Sección interactiva para cargar fotos reales
        st.markdown("---")
        st.markdown("### 📸 Registro Fotográfico del Almacén")
        st.caption("Los operarios pueden tomar fotos a las guías o al estado físico de los estantes y subirlos directamente a la plataforma.")
        archivo_foto = st.file_uploader("Subir foto de control diario (Formato JPG/PNG)", type=["jpg", "png", "jpeg"])
        if archivo_foto is not None:
            st.image(archivo_foto, caption="Vista previa de la captura de control subida con éxito.", use_container_width=True)
