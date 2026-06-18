import streamlit as st
import pandas as pd
import plotly.express as px

# Importación segura de los estilos
try:
    import modulos.estilos as estilos
except ModuleNotFoundError:
    import estilos

def render(sh):
    # 🌎 Control de Idioma
    if "idioma" not in st.session_state:
        st.session_state.idioma = "es"
        
    lang = estilos.obtener_traducciones()[st.session_state.idioma]
    estilos.aplicar_estilos_y_cabecera(st.session_state.idioma)
    
    st.markdown("---")

    # 📊 CARGA DE DATOS DESDE GOOGLE SHEETS
    try:
        ws_inventario = sh.worksheet("inventario")
        df_inv = pd.DataFrame(ws_inventario.get_all_records())
        
        ws_historial = sh.worksheet("historial")
        df_hist = pd.DataFrame(ws_historial.get_all_records())
    except Exception as e:
        st.error(f"❌ Error al cargar datos analíticos: {e}")
        return

    if df_inv.empty:
        st.warning("⚠️ No hay datos de inventario registrados para generar las métricas.")
        return

    # 📈 1. SECCIÓN DE MÉTRICAS CLAVE (KPIs)
    st.markdown("### 🔑 Indicadores Clave / 關鍵指標")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    total_materiales = len(df_inv['Código'].unique())
    stock_total = pd.to_numeric(df_inv['Stock'], errors='coerce').sum()
    almacenes_activos = len(df_inv['Almacén'].unique())

    with col_kpi1:
        st.metric(label="📦 Materiales Únicos / 唯一材料", value=f"{total_materiales} ítems")
    with col_kpi2:
        st.metric(label="🔢 Volumen Total en Stock / 總庫存量", value=f"{int(stock_total):,}")
    with col_kpi3:
        st.metric(label="🏭 Almacenes Operativos / 營運中倉庫", value=almacenes_activos)

    st.markdown("---")

    # 📊 2. GRÁFICOS ANALÍTICOS (Distribución de Stock)
    st.markdown("### 📊 Distribución de Stock por Almacén / 各倉庫庫存分佈")
    
    df_inv['Stock'] = pd.to_numeric(df_inv['Stock'], errors='coerce').fillna(0)
    df_grouped = df_inv.groupby(['Almacén', 'Material'])['Stock'].sum().reset_index()

    # Gráfico interactivo de barras
    fig_stock = px.bar(
        df_grouped, 
        x="Almacén", 
        y="Stock", 
        color="Material",
        title="Cantidad de Materiales Disponibles por Sede",
        barmode="stack",
        template="plotly_white"
    )
    st.plotly_chart(fig_stock, use_container_width=True)

    st.markdown("---")

    # 🐟 3. DIAGRAMA DE ISHIKAWA (Soporte Operativo)
    st.markdown("### 🐟 Análisis de Causa Raíz (Ishikawa) / 📊 魚骨圖原因分析")
    
    with st.expander("🔍 Ver Diagrama de Ishikawa - Control de Desviaciones en Almacén", expanded=False):
        st.markdown("""
        #### **Problema Detectado: Desfase Crítico en los Saldos de Inventario Físico vs. Digital**
        
        * **🧠 Método (方法):**
            * Falta de auditorías cíclicas diarias rápidas.
            * Registro extemporáneo de salidas en los frentes de trabajo de Huaura.
        * **🚜 Maquinaria / Herramientas (設備):**
            * Cortes intermitentes de red móvil en campamentos mineros periféricos.
            * Carga lenta del aplicativo móvil en dispositivos de baja gama.
        * **👤 Mano de Obra (人員):**
            * Omisión involuntaria de registros de devoluciones por parte del personal técnico.
            * Rotación de capataces sin inducción completa sobre el catálogo maestro.
        * **📋 Materiales (材料):**
            * Despacho de materiales sustitutos sin actualización inmediata de código.
            * Deterioro de etiquetas físicas con códigos de barras debido a la humedad ambiental.
        """)

    st.markdown("---")
    st.info("💡 Consejo: Utiliza el menú lateral para registrar nuevos movimientos o cargar auditorías fotográficas Base64.")
