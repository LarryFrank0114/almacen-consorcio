import streamlit as st
import pandas as pd

def inicializar_db():
    """Inicializa la base de datos en la memoria de la sesión si no existe."""
    if 'inventario' not in st.session_state:
        st.session_state.inventario = pd.DataFrame([
            {"Código": "TUB-PE-110", "Material": "Tubería PEAD 110mm (Saneamiento)", "Almacén": "Almacén 6", "Ubicación": "Estante A - Nivel 2", "Stock": 140, "Unidad": "Metros", "Encargado": "Juan Carlos R."},
            {"Código": "VAL-CO-04", "Material": "Válvula de Compuerta 4''", "Almacén": "Almacén 8", "Ubicación": "Pallet 12", "Stock": 25, "Unidad": "Unidades", "Encargado": "Carlos M."},
            {"Código": "ACC-TEE-110", "Material": "Accesorio Tee Inyectada 110mm", "Almacén": "Almacén 10", "Ubicación": "Caja 05", "Stock": 8, "Unidad": "Unidades", "Encargado": "Luis A."}
        ])

def crear_registro(codigo, material, almacen, ubicacion, stock, unidad, encargado):
    df = st.session_state.inventario
    if codigo in df['Código'].values:
        return False, "❌ El código de material ya existe."
    
    nuevo_item = {"Código": codigo, "Material": material, "Almacén": almacen, "Ubicación": ubicacion, "Stock": int(stock), "Unidad": unidad, "Encargado": encargado}
    st.session_state.inventario = pd.concat([df, pd.DataFrame([nuevo_item])], ignore_index=True)
    return True, "✔️ Material registrado con éxito en la base de datos."

def actualizar_registro(codigo, columna, nuevo_valor):
    df = st.session_state.inventario
    idx = df[df['Código'] == codigo].index
    if len(idx) > 0:
        if columna == 'Stock':
            nuevo_valor = int(nuevo_valor)
        st.session_state.inventario.at[idx[0], columna] = nuevo_valor
        return True
    return False

def eliminar_registro(codigo):
    df = st.session_state.inventario
    st.session_state.inventario = df[df['Código'] != codigo].reset_index(drop=True)
    return True
