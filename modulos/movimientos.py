import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh, usuario, modo_lectura=False):
    """
    Módulo de Kardex y Movimientos adaptado a las pestañas reales de Google Sheets.
    """
    
    st.markdown("## 🍄 MOVIMIENTOS DE ALMACÉN (KARDEX)")
    
    # RESPALDO: Si app.py envió el modo lectura por session_state
    if st.session_state.get("modo_lectura_kardex", False):
        modo_lectura = True

    # =======================================================================
    # 📑 1. CARGA DE DATOS DESDE LAS PESTAÑAS REALES (image_c66b85.png)
    # =======================================================================
    try:
        # Vinculación directa con tus pestañas reales de Sheets
        ws_movimientos = sh.worksheet("historial")
        ws_productos = sh.worksheet("inventario")
        
        df_movs = pd.DataFrame(ws_movimientos.get_all_records())
        df_prod = pd.DataFrame(ws_productos.get_all_records())
    except Exception as e:
        st.error(f"❌ Error al conectar con las pestañas de Google Sheets: {e}")
        st.info("💡 Asegúrate de que las pestañas 'historial' e 'inventario' tengan al menos la fila de cabeceras en minúsculas.")
        st.stop()

    # =======================================================================
    # 🔒 2. FILTRADO DE ALMACENES Y ASIGNACIÓN COHERENTE
    # =======================================================================
    usuario_normalizado = str(usuario).lower().strip()
    
    # Definición de Almacenes Autorizados por código para evitar depender de otra pestaña
    if usuario_normalizado == "larry":
        # Eres administrador total: puedes ver todo lo registrado en la columna 'Almacen'
        if not df_movs.empty and "Almacen" in df_movs.columns:
            lista_almacenes = [str(x) for x in df_movs["Almacen"].unique() if str(x).strip() != ""]
            if not lista_almacenes:
                lista_almacenes = ["Almacen Principal"]
        else:
            lista_almacenes = ["Almacen Central", "Almacen Auxiliar"]
    elif usuario_normalizado in ["supervisor", "admin", "piero pezo"]:
        lista_almacenes = ["Almacen Central", "Almacen Auxiliar"]
    else:
        # Responsables asignados dinámicamente a un almacén específico
        if "pezo" in usuario_normalizado:
            lista_almacenes = ["Almacen Auxiliar"]
        else:
            lista_almacenes = ["Almacen Central"]

    almacen_seleccionado = st.selectbox(
        "📦 Selecciona el Almacén a gestionar:",
        lista_almacenes,
        key="kardex_almacen_select"
    )

    # =======================================================================
    # 🛡️ 3. AVISO DE ROLES
    # =======================================================================
    if modo_lectura:
        st.info("ℹ️ **MODO LECTURA ACTIVADO:** Tu rango de Auditoría/Supervisión solo permite visualizar el historial.")
    else:
        st.success(f"🔓 **MODO ESCRITURA:** Conectado como Responsable de: {almacen_seleccionado}")

    # =======================================================================
    # 📝 4. FORMULARIO DE REGISTRO (ESCRIBE EN 'HISTORIAL')
    # =======================================================================
    st.markdown("### 📥 Registrar Nuevo Movimiento")
    
    # Intenta buscar las columnas de productos dinámicamente de tu pestaña 'inventario'
    col_prod_name = "Producto" if "Producto" in df_prod.columns else (df_prod.columns[0] if not df_prod.empty else "Item")
    lista_productos = list(df_prod[col_prod_name].unique()) if not df_prod.empty else ["Item Genérico"]

    with st.form("form_nuevo_movimiento", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            producto = st.selectbox("⭐ Producto / Recurso:", lista_productos, disabled=modo_lectura)
            tipo_mov = st.selectbox("🔄 Tipo de Operación:", ["INGRESO", "SALIDA"], disabled=modo_lectura)
            
        with col2:
            cantidad = st.number_input("🔢 Cantidad:", min_value=1, value=1, step=1, disabled=modo_lectura)
            referencia = st.text_input("📄 N° Guía / Referencia:", placeholder="Ej: GR-00123", disabled=modo_lectura)
            
        with col3:
            destino_origen = st.text_input("🏢 Destino / Procedencia:", placeholder="Ej: Proveedor", disabled=modo_lectura)
            comentario = st.text_area("💬 Notas adicionales:", placeholder="Detalles...", disabled=modo_lectura)
            
        btn_bloqueable = st.form_submit_button("💾 GRABAR MOVIMIENTO EN HISTORIAL", disabled=modo_lectura)
        
        if btn_bloqueable and not modo_lectura:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Formato estándar alineado a las columnas de tu 'historial'
            nueva_fila = [
                fecha_hoy,
                almacen_seleccionado,
                producto,
                tipo_mov,
                cantidad,
                referencia,
                destino_origen,
                comentario,
                usuario
            ]
            
            try:
                ws_movimientos.append_row(nueva_fila)
                st.toast("✅ ¡Registro guardado en la pestaña historial!", icon="🍄")
                st.rerun()
            except Exception as ex:
                st.error(f"Error al escribir en la pestaña historial: {ex}")

    # =======================================================================
    # 📊 5. HISTORIAL DE TRANSACCIONES (MUESTRA LO QUE HAY EN 'HISTORIAL')
    # =======================================================================
    st.markdown("---")
    st.markdown(f"### 📋 Historial de Transacciones - {almacen_seleccionado}")

    if not df_movs.empty:
        # Limpiar espacios en cabeceras de columnas
        df_movs.columns = [c.strip() for c in df_movs.columns]
        
        # Filtrar por almacén si existe la columna correspondiente
        col_almacen = "Almacen" if "Almacen" in df_movs.columns else (df_movs.columns[1] if len(df_movs.columns) > 1 else "")
        
        if col_almacen in df_movs.columns:
            df_filtrado = df_movs[df_movs[col_almacen] == almacen_seleccionado]
        else:
            df_filtrado = df_movs.copy()
            
        if not df_filtrado.empty:
            # Ordenar por fecha para tener lo más nuevo arriba
            col_fecha = "Fecha" if "Fecha" in df_filtrado.columns else df_filtrado.columns[0]
            try:
                df_filtrado = df_filtrado.sort_values(by=col_fecha, ascending=False)
            except:
                pass
                
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            # Cálculo de totales rápidos para las métricas de control
            col_tipo = "Tipo_Movimiento" if "Tipo_Movimiento" in df_filtrado.columns else (df_filtrado.columns[3] if len(df_filtrado.columns) > 3 else "")
            col_cant = "Cantidad" if "Cantidad" in df_filtrado.columns else (df_filtrado.columns[4] if len(df_filtrado.columns) > 4 else "")
            
            if col_tipo in df_filtrado.columns and col_cant in df_filtrado.columns:
                total_ingresos = pd.to_numeric(df_filtrado[df_filtrado[col_tipo] == "INGRESO"][col_cant], errors='coerce').sum()
                total_salidas = pd.to_numeric(df_filtrado[df_filtrado[col_tipo] == "SALIDA"][col_cant], errors='coerce').sum()
                
                c_res1, c_res2 = st.columns(2)
                c_res1.metric(label="🟢 Total Items Ingresados", value=int(total_ingresos))
                c_res2.metric(label="🔴 Total Items Despachados", value=int(total_salidas))
        else:
            st.info(f"No se registran transacciones para el {almacen_seleccionado} en la pestaña historial.")
    else:
        st.info("La pestaña 'historial' se encuentra vacía.")
