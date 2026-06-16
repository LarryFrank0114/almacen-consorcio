import streamlit as st
import pandas as pd

def render(sh):
    st.markdown("### Reporte de Stock Consolidado")
    st.markdown("Monitoreo de existencias de materiales autorizados.")
    st.markdown("---")
    
    # Intentar leer la pestaña "inventario" de Google Sheets
    try:
        ws_inv = sh.worksheet("inventario")
        df_inv = pd.DataFrame(ws_inv.get_all_records())
    except Exception as e:
        st.error(f"❌ Error al leer el inventario desde Google Sheets: {e}")
        return

    # Verificar si el DataFrame está vacío
    if df_inv.empty:
        st.warning("⚠️ La pestaña 'inventario' no contiene registros o filas de datos.")
        return

    # Filtros superiores limpios y minimalistas
    col1, col2 = st.columns(2)
    with col1:
        filtro_almacen = st.multiselect(
            "Filtrar por Sede:", 
            options=df_inv['Almacén'].unique(), 
            default=df_inv['Almacén'].unique()
        )
    with col2:
        buscar = st.text_input("Buscar recurso (Nombre o Código):")

    # Aplicar filtros a la tabla
    df_filtrado = df_inv[df_inv['Almacén'].isin(filtro_almacen)]
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado['Material'].astype(str).str.contains(buscar, case=False) | 
            df_filtrado['Código'].astype(str).str.contains(buscar, case=False)
        ]

    # Alerta de Stock Crítico
    if 'Stock' in df_filtrado.columns:
        materiales_criticos = df_filtrado[df_filtrado['Stock'].astype(int) <= 5]
        if not materiales_criticos.empty:
            st.error(f"🚨 **Stock Crítico Detectado (≤ 5 unidades):** Existen {len(materiales_criticos)} artículos en riesgo de quiebre.")
            with st.expander("Ver Lista de Artículos Críticos"):
                st.table(materiales_criticos[['Almacén', 'Código', 'Material', 'Stock']])
            
    # Render de la tabla principal de existencias
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # ==========================================
    # PANEL DE EDICIÓN EXCLUSIVO PARA ADMINISTRADORES
    # ==========================================
    if st.session_state.user_role == "Administrador":
        st.markdown("---")
        st.markdown("### Panel de Corrección Logística")
        
        almacen_crud_sel = st.selectbox(
            "1. Seleccione Almacén a modificar:", 
            options=["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"]
        )
        
        # Filtrar materiales que pertenecen exclusivamente a la sede seleccionada
        materiales_en_almacen = df_inv[df_inv['Almacén'].astype(str) == almacen_crud_sel]
        
        if not materiales_en_almacen.empty:
            # 🔥 SOLUCIÓN AL ERROR DE NUMPY: Forzamos .astype(str) a cada columna antes de concatenar
            codigos_str = materiales_en_almacen['Código'].astype(str)
            nombres_str = materiales_en_almacen['Material'].astype(str)
            opciones_combo = codigos_str + " - " + nombres_str
            
            material_crud = st.selectbox("2. Seleccione el Material a modificar:", options=opciones_combo)
            
            # Extraer el código limpio separando por el guion
            codigo_seleccionado = material_crud.split(" - ")[0]
            datos_material = materiales_en_almacen[materiales_en_almacen['Código'].astype(str) == codigo_seleccionado].iloc[0]
            
            # Formulario de edición rápida alineado de forma impecable
            with st.form("form_edicion_rapida"):
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    nuevo_stock = st.number_input("Stock Real:", value=int(datos_material['Stock']), min_value=0)
                with col_e2:
                    nueva_ubica = st.text_input("Ubicación Interna:", value=str(datos_material['Ubicación']))
                with col_e3:
                    nuevo_encargado = st.text_input("Custodio:", value=str(datos_material['Encargado']))
                    
                boton_guardar = st.form_submit_button("Guardar Cambios en la Nube")
                
                if boton_guardar:
                    todos_los_datos = ws_inv.get_all_records()
                    fila_editar = None
                    # Buscar la fila exacta en Google Sheets
                    for idx, fila in enumerate(todos_los_datos):
                        if str(fila['Almacén']) == almacen_crud_sel and str(fila['Código']) == codigo_seleccionado:
                            fila_editar = idx + 2  # +2 por el encabezado de la hoja de cálculo
                            break
                            
                    if fila_editar:
                        ws_inv.update_cell(fila_editar, 5, nuevo_stock)      # Columna E: Stock
                        ws_inv.update_cell(fila_editar, 4, nueva_ubica)      # Columna D: Ubicación
                        ws_inv.update_cell(fila_editar, 7, nuevo_encargado)  # Columna G: Encargado
                        st.success("✔️ Ficha de inventario actualizada con éxito en Google Sheets.")
                        st.rerun()
                    else:
                        st.error("❌ No se encontró la coordenada de fila del material en la base de datos.")
        else:
            st.info("ℹ️ No hay materiales registrados actualmente en esta sede.")

    # ==========================================
    # CARGA DE IMÁGENES RESTRINGIDA EXCLUSIVA PARA LARRY
    # ==========================================
    if st.session_state.username == "Larry Rodriguez - Jefe de Almacenes Externos":
        st.markdown("---")
        st.markdown("### Control Visual de Sede (Exclusivo Jefatura)")
        st.info("Larry, aquí puedes registrar y archivar el reporte fotográfico de las condiciones físicas del almacén.")
        
        almacen_foto = st.selectbox("Sede a reportar fotográficamente:", ["Almacén 1", "Almacén 6", "Almacén 8", "Almacén 10"], key="foto_almacen_key")
        imagen_cargada = st.file_uploader("Subir captura de control de almacén (.png, .jpg)", type=["png", "jpg", "jpeg"])
        
        if imagen_cargada is not None:
            st.image(imagen_cargada, caption=f"Vista previa para {almacen_foto}", width=400)
            if st.button("Confirmar y Archivar Registro Visual"):
                st.success
