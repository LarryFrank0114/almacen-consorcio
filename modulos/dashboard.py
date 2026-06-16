import streamlit as st
import pandas as pd

def render(sh):
    st.markdown("### Dashboard Gerencial")
    st.markdown("Indicadores clave del flujo logístico y transacciones registradas en tiempo real.")
    
    try:
        ws_historial = sh.worksheet("historial")
        df_historial = pd.DataFrame(ws_historial.get_all_records())
    except Exception:
        df_historial = pd.DataFrame()
        
    if df_historial.empty:
        st.info("No se registran movimientos transaccionales en el historial.")
        return
        
    total_movs = len(df_historial)
    ingresos = len(df_historial[df_historial['Tipo'].astype(str).str.contains('INGRESO|Ingreso', case=False, na=False)])
    salidas = len(df_historial[df_historial['Tipo'].astype(str).str.contains('SALIDA|Egreso|Salida', case=False, na=False)])
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.markdown(f"<div class='kpi-card kpi-total'><div class='kpi-number' style='color:#134074;'>{total_movs}</div><div class='kpi-label'>📋 Total Operaciones</div></div>", unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"<div class='kpi-card kpi-ingreso'><div class='kpi-number' style='color:#2E7D32;'>📥 {ingresos}</div><div class='kpi-label'>Ingresos (Guías)</div></div>", unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f"<div class='kpi-card kpi-salida'><div class='kpi-number' style='color:#C62828;'>📤 {salidas}</div><div class='kpi-label'>Salidas (Vales)</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### **Actividad por Almacén**")
        if 'Almacén' in df_historial.columns:
            st.bar_chart(df_historial['Almacén'].value_counts(), color="#134074")
    with col_g2:
        st.markdown("##### **Frecuencia Cronológica**")
        if 'Fecha' in df_historial.columns:
            st.line_chart(df_historial['Fecha'].value_counts().sort_index(), color="#F57C00")
