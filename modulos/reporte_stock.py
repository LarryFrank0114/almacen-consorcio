import streamlit as st
import pandas as pd

def render(sh):
    st.markdown("""
        <h2 style='text-align: center; color: #FBD000; font-family: "Press Start 2P"; font-size: 16px; margin-bottom: 20px;'>
            📦 STOCKS CONSOLIDADOS - MUNDO CENTRAL
        </h2>
    """, unsafe_allow_html=True)

    try:
        # 1. Conexión exacta a la pestaña 'inventario' de Google Sheets
        hoja_stock = sh.worksheet("inventario")
        datos_raw = hoja_stock.get_all_records()
        
        if not datos_raw:
            st.warning("⚠️ No se encontraron registros en la pestaña 'inventario'.")
            return
            
        df = pd.DataFrame(datos_raw)

        # =======================================================================
        # 🔍 SISTEMA DE FILTRADO EN TIEMPO REAL
        # =======================================================================
        st.markdown("<p style='color: #FBD000; margin-bottom: 5px;'>🔍 SISTEMA DE BÚSQUEDA:</p>", unsafe_allow_html=True)
        
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            # Filtro por Código (Soporta números o texto)
            filtro_codigo = st.text_input("Filtrar por Código:", value="", key="search_codigo")
            
        with col_filtro2:
            # Filtro por descripción del Material
            filtro_material = st.text_input("Filtrar por Material:", value="", key="search_material")
        
        # Aplicación de los filtros sobre el DataFrame original
        df_filtrado = df.copy()
        
        if filtro_codigo:
            df_filtrado = df_filtrado[df_filtrado['Código'].astype(str).str.contains(filtro_codigo.strip(), case=False, na=False)]
            
        if filtro_material:
            df_filtrado = df_filtrado[df_filtrado['Material'].astype(str).str.contains(filtro_material.strip(), case=False, na=False)]

        st.markdown("<p style='color: #43B047; margin-top: 15px;'>📝 Puedes editar las celdas de 'Stock' directamente en la tabla:</p>", unsafe_allow_html=True)

        # =======================================================================
        # 📊 EDITOR DE DATOS INTERACTIVO (STREAMLIT DATA EDITOR)
        # =======================================================================
        # Deshabilitamos la edición en todas las columnas excepto en 'Stock' para proteger los datos maestros
        df_editado = st.data_editor(
            df_filtrado,
            use_container_width=True,
            num_rows="fixed",
            disabled=["Código", "Material", "Almacén", "Ubicación", "Unidad", "Encargado"],
            key="editor_tabla_inventario"
        )

        # =======================================================================
        # 💾 GUARDAR CAMBIOS DE FORMA SEGURA EN GOOGLE SHEETS
        # =======================================================================
        if st.button("💾 GUARDAR CAMBIOS EN SHEETS", use_container_width=True):
            con_errores = False
            cambios_detectados = 0
            
            # Recorremos el DataFrame editado para buscar diferencias respecto al original
            for idx, fila_editada in df_editado.iterrows():
                # El índice original de la fila nos dice su posición real en el DataFrame maestro 'df'
                fila_original = df.iloc[idx]
                
                val_original = fila_original.get("Stock", 0)
                val_editado = fila_editada.get("Stock", 0)
                
                # Si el valor de la celda cambió, procedemos a actualizar Sheets
                if str(val_original).strip() != str(val_editado).strip():
                    cambios_detectados += 1
                    
                    # La fila en Google Sheets es: índice_fila_dataframe + 2 (1 por índice 0 y 1 por encabezados)
                    num_fila_sheets = int(idx) + 2 
                    
                    # --- RESISTENCIA AL ERROR '0.00' ---
                    try:
                        # Convertimos primero a float para limpiar el string '0.00' y luego a un entero puro
                        cantidad_limpia = int(float(str(val_editado).strip()))
                    except (ValueError, TypeError):
                        st.error(f"❌ Error en la fila {num_fila_sheets} ('{fila_editada.get('Material')}'): El valor '{val_editado}' no es válido.")
                        con_errores = True
                        continue

                    # Identificamos la columna exacta de 'Stock' dinámicamente en Google Sheets
                    try:
                        if "Stock" in df.columns:
                            pos_columna_stock = df.columns.get_loc("Stock") + 1
                            # Escritura directa en celda específica
                            hoja_stock.update_cell(num_fila_sheets, pos_columna_stock, cantidad_limpia)
                        else:
                            st.error("❌ No se encontró la columna 'Stock' en la estructura de la tabla.")
                            con_errores = True
                            break
                    except Exception as ex_sheet:
                        st.error(f"❌ Error de red al guardar en la fila {num_fila_sheets}: {ex_sheet}")
                        con_errores = True
                        break

            if cambios_detectados == 0:
                st.info("ℹ️ No se detectó ninguna modificación en los valores de Stock para guardar.")
            elif not con_errores:
                st.success(f"🍄 ¡Sincronización Exitosa! Se actualizaron {cambios_detectados} registros en la pestaña 'inventario'.")
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error crítico al cargar el módulo de Stock: {e}")
