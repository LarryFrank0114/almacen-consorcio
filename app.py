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

# Enrutador de pantallas (Añadir el caso de la auditoría)
sh = db.conectar_sheets()

if menu == "Inicio":
    home.render()
elif menu == "Panel de Control":
    dashboard.render(sh)
elif menu == "Stock Consolidados":
    reporte_stock.render(sh)
elif menu == "Movimientos (Kardex)":
    movimientos.render(sh)
elif menu == "Auditoría de Terreno":
    auditoria.render(sh)  # <- Aquí mandamos a llamar el nuevo módulo operativo
elif menu == "Ajustes del Sistema":
    ajustes.render(sh)
