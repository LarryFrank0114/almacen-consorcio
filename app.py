import streamlit as st
import database as db
# Asegúrate de añadir ", auditoria" en tus importaciones de módulos
from modulos import home, dashboard, reporte_stock, movimientos, ajustes, auditoria

# ... (Tu código de configuración inicial, login y sesión de app.py se mantiene exactamente igual)

# Modificar el menú de navegación de la barra lateral
with st.sidebar:
    st.markdown("### 🛠️ Sistema de Gestión")
    menu = st.radio(
        "Seleccione un Módulo:",
        ["Inicio", "Panel de Control", "Stock Consolidados", "Movimientos (Kardex)", "Auditoría de Terreno", "Ajustes del Sistema"]
    )
    st.markdown("---")

# Enrutador de pantallas corregido
sh = db.conectar_sheets()

if menu == "Inicio":
    try:
        home.render() # Si te sigue dando error aquí, cámbialo por: home.render(sh)
    except TypeError:
        home.render(sh)
elif menu == "Panel de Control":
    dashboard.render(sh)
elif menu == "Stock Consolidados":
    reporte_stock.render(sh)
elif menu == "Movimientos (Kardex)":
    movimientos.render(sh)
elif menu == "Auditoría de Terreno":
    auditoria.render(sh)  
elif menu == "Ajustes del Sistema":
    ajustes.render(sh)
