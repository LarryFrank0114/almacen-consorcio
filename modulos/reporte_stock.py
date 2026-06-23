import streamlit as st
import pandas as pd

def render(sh):
    st.markdown("""
        <h2 style='text-align: center; color: #FBD000; font-family: "Press Start 2P"; font-size: 16px;'>
            📦 STOCKS CONSOLIDADOS - MUNDO CENTRAL
        </h2>
    """, unsafe_allow_html=True)

    try:
        # 1. Conectar a la pestaña correspondiente en Google Sheets
        hoja_stock = sh.worksheet("inventario")
        datos_raw = hoja_stock.get_all_records()
        
        if not datos_raw:
            st.warning("⚠️ No se encontraron registros en la base de datos de Stock.")
            return
            
        df = pd.DataFrame(datos_raw)

        st.markdown("<p style='color: #43B047;'>📝 Puedes editar las cantidades directamente en la tabla inferior:</p>", unsafe_allow_html=True)

        # 2. Renderizar el editor de datos interactivo de Streamlit
        # Asumiendo columnas típicas: ['ID', 'Producto', 'Almacen', 'Cantidad']
        df_editado = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed",
            key="editor_tabla_stock"
        )

        # 3. Detectar si el usuario realizó cambios manuales en la tabla
        if st.button("💾 GUARDAR CAMBIOS EN SHEETS", use_container_width=True):
            con_errores = False
            
            # Recorremos fila por fila para validar y actualizar
            for idx, fila in df_editado.iterrows():
                # Obtenemos el ID o identificador único de la fila (usualmente en la columna 1, índice 0)
                # Y localizamos la fila correspondiente en Google Sheets (sumamos 2 por el encabezado index-1)
                num_fila_sheets = idx + 2 
                
                # --- SOLUCIÓN INTEGRAL AL ERROR '0.00' ---
                try:
                    # Capturamos el valor editado de la columna 'Cantidad'
                    cantidad_original = fila.get("Cantidad", 0)
                    
                    # Forzamos la conversión a float primero para limpiar cadenas como '0.00' o '15.00'
                    # Luego lo convertimos a un entero limpio para guardarlo de manera óptima
                    cantidad_limpia = int(float(str(cantidad_original).strip()))
                    
                except (ValueError, TypeError):
                    st.error(f"❌ Error en la fila {num_fila_sheets}: El valor '{cantidad_original}' no es un número válido.")
                    con_errores = True
                    continue

                # Identificamos en qué columna de Google Sheets está 'Cantidad'
                # Si tu columna 'Cantidad' es la tercera (C), el índice de columna en Sheets es 3
                try:
                    pos_columna_cantidad = df.columns.get_loc("Cantidad") + 1
                    
                    # Actualizamos únicamente la celda que cambió con el entero limpio
                    hoja_stock.update_cell(num_fila_sheets, pos_columna_cantidad, cantidad_limpia)
                except Exception as ex_sheet:
                    st.error(f"❌ Error al escribir en Google Sheets (Fila {num_fila_sheets}): {ex_sheet}")
                    con_errores = True
                    break

            if not con_errores:
                st.success("🍄 ¡Datos de Stock sincronizados y guardados con éxito en Google Sheets!")
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error crítico al cargar el módulo de Stock: {e}")
