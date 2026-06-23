import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh, usuario, modo_lectura=False):
    """
    Módulo de Kardex parametrizado por Responsable de Almacén Oficial y Filtros de Seguridad.
    """
    st.markdown("## 🍄 MOVIMIENTOS DE ALMACÉN (KARDEX)")
    
    usuario_normalizado = str(usuario).lower().strip()

    # =======================================================================
    # 📑 1. CARGA DE RECURSOS DESDE PESTAÑAS REALES (image_c66b85.png)
    # =======================================================================
    try:
        ws_movimientos = sh.worksheet("historial")
        ws_productos = sh.worksheet("inventario")
        
        df_movs = pd.DataFrame(ws_movimientos.get_all_records())
        df_prod = pd.DataFrame(ws_productos.get_all_records())
    except Exception as e:
        st.error(f"❌ Error al mapear las pestañas de Google Sheets: {e}")
        st.stop()

    # =======================================================================
    # 🔒 2. MATRIZ OPERATIVA DE ASIGNACIÓN DE ALMACENES
    # =======================================================================
    # Larry tiene acceso y control absoluto sobre todas las locaciones existentes
    if usuario_normalizado == "larry":
        lista_almacenes = ["Almacén 01", "Almacén 06", "Almacén 08", "Almacén 10"]
    else:
        # Enrutamiento estricto por responsable según definición del Consorcio
        mapeo_almacenes = {
            "piero pezo": ["Almacén 10"],
            "gregorio rodriguez": ["Almacén 01"],
            "marcial huayta": ["Almacén 08"],
            "enrique sanchez": ["Almacén 06"]
        }
        # Si el usuario es de supervisión o gerencia china, ve todos para modo lectura; si no, su almacén asignado
        if modo_lectura:
            lista_almacenes = ["Almacén 01", "Almacén 06", "Almacén 08", "Almacén 10"]
        else:
            lista_almacenes = mapeo_almacenes.get(usuario_normalizado, ["Almacén 01"])

    almacen_seleccionado = st.selectbox(
        "📦 Selecciona el Almacén a gestionar:",
        lista_almacenes,
        key="kardex_almacen_select"
    )

    # =======================================================================
    # 🛡️ 3. VISUALIZACIÓN DE ALERTAS DE RANGO Y SEGURIDAD
    # =======================================================================
    if modo_lectura:
        st.info("ℹ️ **MODO LECTURA (SUPERVISIÓN / GERENCIA CHINA):** Toda la plataforma se encuentra bloqueada contra modificaciones o alteración de recursos.")
    else:
        st.success(f"🔓 **MODO OPERATIVO ACTIVO:** Documentando ingresos y egresos para el **{almacen_seleccionado}**")

    # =======================================================================
    # 📥 4. CARGA DE DOCUMENTOS E INGRESOS/EGRESOS POR ALMACÉN
    # =======================================================================
    st.markdown(f"### 📥 Cargar Documento de Movimiento - {almacen_seleccionado}")
    
    col_prod_name = "Producto" if "Producto" in df_prod.columns else (df_prod.columns[0] if not df_prod.empty else "Item")
    lista_productos = list(df_prod[col_prod_name].unique()) if not df_prod.empty else ["Material Genérico"]

    with st.form("form_nuevo_movimiento", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            producto = st.selectbox("⭐ Recurso / Material:", lista_productos, disabled=modo_lectura)
            tipo_mov = st.selectbox("🔄 Tipo de Flujo:", ["INGRESO", "SALIDA"], disabled=modo_lectura)
            
        with col2:
            cantidad = st.number_input("🔢 Cantidad Física:", min_value=1, value=1, step=1, disabled=modo_lectura)
            referencia = st.text_input("📄 N° Guía de Remisión / Documento:", placeholder="Ej: GR-010-00234", disabled=modo_lectura)
            
        with col3:
            destino_origen = st.text_input("🏢 Destino u Origen del Recurso:", placeholder="Ej: Frente de Obra / Proveedor Central", disabled=modo_lectura)
            comentario = st.text_area("💬 Observaciones:", placeholder="Escribe notas sobre el estado o uso del material...", disabled=modo_lectura)
            
        btn_grabar = st.form_submit_button("💾 TRANSMITIR DOCUMENTO A HISTORIAL", disabled=modo_lectura)
        
        if btn_grabar and not modo_lectura:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Estructura alineada e inyectada de forma segura
            nueva_fila = [
                fecha_hoy,
                almacen_seleccionado,
                producto,
                tipo_mov,
                cantidad,
                referencia,
                destino_origen,
                comentario,
                usuario.upper()
            ]
            
            try:
                ws_movimientos.append_row(nueva_fila)
                st.toast(f"✅ Documento anexado con éxito al {almacen_seleccionado}", icon="🍄")
                st.rerun()
            except Exception as ex:
                st.error(f"Error de red al actualizar la base de datos: {ex}")

    # =======================================================================
    # 📊 5. HISTORIAL DE RECURSOS ASIGNADOS AL ALMACÉN
    # =======================================================================
    st.markdown("---")
    st.markdown(f"### 📋 Transacciones y Registros Recientes - {almacen_seleccionado}")

    if not df_movs.empty:
        df_movs.columns = [c.strip() for c in df_movs.columns]
        
        # Encontrar la columna del almacén de manera dinámica en la hoja 'historial'
        col_almacen = "Almacen" if "Almacen" in df_movs.columns else (df_movs.columns[1] if len(df_movs.columns) > 1 else "")
        
        if col_almacen in df_movs.columns:
            # Filtrado preciso: los encargados solo ven la data de su propio almacén
            df_filtrado = df_movs[df_movs[col_almacen] == almacen_seleccionado]
        else:
            df_filtrado = df_movs.copy()
            
        if not df_filtrado.empty:
            col_fecha = "Fecha" if "Fecha" in df_filtrado.columns else df_filtrado.columns[0]
            try:
                df_filtrado = df_filtrado.sort_values(by=col_fecha, ascending=False)
            except:
                pass
                
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            col_tipo = "Tipo_Movimiento" if "Tipo_Movimiento" in df_filtrado.columns else (df_filtrado.columns[3] if len(df_filtrado.columns) > 3 else "")
            col_cant = "Cantidad" if "Cantidad" in df_filtrado.columns else (df_filtrado.columns[4] if len(df_filtrado.columns) > 4 else "")
            
            if col_tipo in df_filtrado.columns and col_cant in df_filtrado.columns:
                total_ingresos = pd.to_numeric(df_filtrado[df_filtrado[col_tipo] == "INGRESO"][col_cant], errors='coerce').sum()
                total_salidas = pd.to_numeric(df_filtrado[df_filtrado[col_tipo] == "SALIDA"][col_cant], errors='coerce').sum()
                
                c_res1, c_res2 = st.columns(2)
                c_res1.metric(label="🟢 Volumen Total de Ingresos", value=int(total_ingresos))
                c_res2.metric(label="🔴 Volumen Total de Egresos", value=int(total_salidas))
        else:
            st.info(f"No se registran transacciones previas cargadas para el {almacen_seleccionado} en la base de datos.")
    else:
        st.info("La hoja de historial se encuentra lista y esperando registros.")
