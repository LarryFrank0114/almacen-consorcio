import streamlit as st
import pandas as pd

def inicializar_db():
    """Inicializa las estructuras de datos globales en la sesión de Streamlit."""
    
    # 1. Maestro único de materiales de saneamiento
    if 'maestro_materiales' not in st.session_state:
        st.session_state.maestro_materiales = pd.DataFrame([
            {"Código": "TUB-PE-110", "Material": "Tubería PEAD 110mm", "Unidad": "Metros"},
            {"Código": "VAL-CO-04", "Material": "Válvula de Compuerta de 4 Pulgadas", "Unidad": "Unidades"},
            {"Código": "ACC-TEE-110", "Material": "Accesorio Tee Inyectada 110mm", "Unidad": "Unidades"},
            {"Código": "HID-PO-02", "Material": "Hidrante de Poste Completo", "Unidad": "Unidades"}
        ])

    # 2. Inventario físico consolidado por sede (Stock Actual)
    if 'inventario' not in st.session_state:
        st.session_state.inventario = pd.DataFrame([
            {"Código": "TUB-PE-110", "Material": "Tubería PEAD 110mm", "Almacén": "Almacén 6", "Ubicación": "Estante A - Nivel 2", "Stock": 140, "Unidad": "Metros", "Encargado": "Juan Carlos R."},
            {"Código": "VAL-CO-04", "Material": "Válvula de Compuerta de 4 Pulgadas", "Almacén": "Almacén 8", "Ubicación": "Pallet 12", "Stock": 25, "Unidad": "Unidades", "Encargado": "Carlos M."},
            {"Código": "ACC-TEE-110", "Material": "Accesorio Tee Inyectada 110mm", "Almacén": "Almacén 10", "Ubicación": "Caja 05", "Stock": 8, "Unidad": "Unidades", "Encargado": "Luis A."},
            {"Código": "TUB-PE-110", "Material": "Tubería PEAD 110mm", "Almacén": "Almacén 1", "Ubicación": "Zona Patio A", "Stock": 50, "Unidad": "Metros", "Encargado": "Ing. Eduardo T."}
        ])

    # 3. Historial de movimientos transaccionales para auditoría y Dashboard
    if 'historial_movimientos' not in st.session_state:
        st.session_state.historial_movimientos = pd.DataFrame([
            {
                "Fecha": "2026-06-01", "Tipo": "Egreso (Vale de Salida)", "Documento": "V-001", "Almacén": "Almacén 6",
                "Solicitante": "Téc. Operativo", "Supervisor": "Ing. Marcos Silva", "Código": "TUB-PE-110",
                "Material": "Tubería PEAD 110mm", "Cantidad": 20, "Unidad": "Metros", "Encargado": "Juan Carlos R.", "Observaciones": "Frente SJM Sector 3"
            },
            {
                "Fecha": "2026-06-10", "Tipo": "Egreso (Vale de Salida)", "Documento": "V-002", "Almacén": "Almacén 8",
                "Solicitante": "Téc. Conexiones", "Supervisor": "Ing. Laura Benites", "Código": "VAL-CO-04",
                "Material": "Válvula de Compuerta de 4 Pulgadas", "Cantidad": 5, "Unidad": "Unidades", "Encargado": "Carlos M.", "Observaciones": "Frente VMT Sector 1"
            },
            {
                "Fecha": "2026-05-15", "Tipo": "Egreso (Vale de Salida)", "Documento": "V-003", "Almacén": "Almacén 1",
                "Solicitante": "Cuadrilla A", "Supervisor": "Ing. Marcos Silva", "Código": "TUB-PE-110",
                "Material": "Tubería PEAD 110mm", "Cantidad": 15, "Unidad": "Metros", "Encargado": "Ing. Eduardo T.", "Observaciones": "Frente VES Av. Central"
            }
        ])

def registrar_transaccion(tipo_mov, doc, almacen, fecha, solicitante, supervisor, encargado, observaciones, lista_recursos):
    """Procesas ingresos y egresos de múltiples recursos de forma simultánea mitigando errores de stock."""
    df_inv = st.session_state.inventario
    df_hist = st.session_state.historial_movimientos
    nuevos_movimientos = []

    if tipo_mov == "Egreso (Vale de Salida)":
        for rec in lista_recursos:
            idx = df_inv[(df_inv['Código'] == rec['Código']) & (df_inv['Almacén'] == almacen)].index
            stock_actual = df_inv.at[idx[0], 'Stock'] if len(idx) > 0 else 0
            if stock_actual < rec['Cantidad']:
                return False, f"❌ Stock insuficiente de {rec['Material']} en {almacen}. Disponible: {stock_actual}"

    for rec in lista_recursos:
        idx = df_inv[(df_inv['Código'] == rec['Código']) & (df_inv['Almacén'] == almacen)].index
        
        if len(idx) > 0:
            stock_actual = df_inv.at[idx[0], 'Stock']
            if tipo_mov == "Egreso (Vale de Salida)":
                df_inv.at[idx[0], 'Stock'] = stock_actual - rec['Cantidad']
            else:
                df_inv.at[idx[0], 'Stock'] = stock_actual + rec['Cantidad']
        else:
            nuevo_stock_item = {
                "Código": rec['Código'], "Material": rec['Material'], "Almacén": almacen,
                "Ubicación": "Por Asignar", "Stock": rec['Cantidad'], "Unidad": rec['Unidad'], "Encargado": encargado
            }
            df_inv = pd.concat([df_inv, pd.DataFrame([nuevo_stock_item])], ignore_index=True)

        mov = {
            "Fecha": str(fecha), "Tipo": tipo_mov, "Documento": doc, "Almacén": almacen,
            "Solicitante": solicitante, "Supervisor": supervisor, "Código": rec['Código'],
            "Material": rec['Material'], "Cantidad": rec['Cantidad'], "Unidad": rec['Unidad'],
            "Encargado": encargado, "Observaciones": observaciones
        }
        nuevos_movimientos.append(mov)

    st.session_state.inventario = df_inv
    st.session_state.historial_movimientos = pd.concat([df_hist, pd.DataFrame(nuevos_movimientos)], ignore_index=True)
    return True, f"✔️ Transacción {doc} procesada con éxito con {len(lista_recursos)} recurso(s)."
