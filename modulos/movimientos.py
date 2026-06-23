import streamlit as st
import pandas as pd
from datetime import datetime

def render(sh, usuario, modo_lectura=False):
    """
    Módulo de Kardex y Movimientos de Almacén.
    
    Parámetros:
    - sh: Conexión activa a Google Sheets.
    - usuario: Nombre del usuario logueado (para filtrar almacenes autorizados).
    - modo_lectura: Booleano que deshabilita la escritura para supervisores/auditores.
    """
    
    st.markdown("## 🍄 MOVIMIENTOS DE ALMACÉN (KARDEX)")
    
    # RESPALDO: Si app.py envió el modo lectura por session_state
    if st.session_state.get("modo_lectura_kardex", False):
        modo_lectura = True

    # =======================================================================
    # 📑 1. CARGA DE DATOS DESDE GOOGLE SHEETS
    # =======================================================================
    try:
        # Hojas recomendadas en tu sistema de Almacén Consorcio
        ws_movimientos = sh.worksheet("Movimientos")
        ws_usuarios = sh.worksheet("Usuarios") # Hoja con columnas: Usuario, Almacen_Autorizado
        ws_productos = sh.worksheet("Productos")
        
        df_movs = pd.DataFrame(ws_movimientos.get_all_records())
        df_users = pd.DataFrame(ws_usuarios.get_all_records())
        df_prod = pd.DataFrame(ws_productos.get_all_records())
    except Exception as e:
        st.error(f"❌ Error al conectar con las tablas del almacén: {e}")
        st.stop()

    # =======================================================================
    # 🔒 2. FILTRADO DE ALMACENES SEGÚN RESPONSABLE
    # =======================================================================
    usuario_normalizado = str(usuario).lower().strip()
    
    # Si eres el administrador principal (Larry), tienes acceso a TODOS los almacenes
    if usuario_normalizado == "larry":
        if not df_movs.empty and "Almacen" in df_movs.columns:
            lista_almacenes = list(df_movs["Almacen"].unique())
        else:
            lista_almacenes = ["Almacen Central", "Almacen Auxiliar"]
    else:
        # Buscar qué almacén tiene autorizado este responsable en la hoja de Usuarios
        filtro_user = df_users[df_users["Usuario"].str.lower().str.strip() == usuario_normalizado]
        
        if not filtro_user.empty:
            lista_almacenes = [filtro_user.iloc[0]["Almacen_Autorizado"]]
        else:
            # Almacén de contingencia por si no está explícito en la lista
            lista_almacenes = ["Almacen Central"]
            st.warning(f"⚠️ Usuario '{usuario}' no tiene un almacén asignado en la base de datos. Usando {lista_almacenes[0]} por defecto.")

    # Selector de almacén (Filtrado según permisos)
    almacen_seleccionado = st.selectbox(
        "📦 Selecciona el Almacén a gestionar:",
        lista_almacenes,
        key="kardex_almacen_select"
    )

    # =======================================================================
    # 🛡️ 3. AVISO DE ROL Y MODO DE LECTURA
    # =======================================================================
    if modo_lectura:
        st.info("ℹ️ **MODO LECTURA ACTIVADO:** Tu cuenta (Supervisión / Auditoría) solo permite visualizar el historial de recursos sin realizar alteraciones.")
    else:
        st.success(f"🔓 **MODO ESCRITURA:** Conectado como Responsable autorizado de: {almacen_seleccionado}")

    # =======================================================================
    # 📝 4. FORMULARIO DE REGISTRO (SOLO ESCRITURA)
    # =======================================================================
    st.markdown("### 📥 Registrar Nuevo Movimiento (Ingreso / Salida)")
    
    # Lista de productos para el combo
    lista_productos = list(df_prod["Producto"].unique()) if not df_prod.empty and "Producto" in df_prod.columns else ["Item Generico"]

    with st.form("form_nuevo_movimiento", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            producto = st.selectbox("⭐ Producto / Recurso:", lista_productos, disabled=modo_lectura)
            tipo_mov = st.selectbox("🔄 Tipo de Operación:", ["INGRESO", "SALIDA"], disabled=modo_lectura)
            
        with col2:
            cantidad = st.number_input("🔢 Cantidad:", min_value=1, value=1, step=1, disabled=modo_lectura)
            referencia = st.text_input("📄 N° Guía / Referencia:", placeholder="Ej: GR-00123", disabled=modo_lectura)
            
        with col3:
            destino_origen = st.text_input("🏢 Destino / Procedencia:", placeholder="Ej: Proveedor SAC / Frente 1", disabled=modo_lectura)
            comentario = st.text_area("💬 Notas adicionales:", placeholder="Detalles del estado de la carga...", disabled=modo_lectura)
            
        # El botón de guardar se congela por completo si 'modo_lectura' es True
        btn_bloqueable = st.form_submit_button("💾 GRABAR MOVIMIENTO EN KARDEX", disabled=modo_lectura)
        
        if btn_bloqueable and not modo_lectura:
            if producto and cantidad > 0:
                # Preparar la nueva fila con la estampa de tiempo actual
                fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                    st.toast("✅ ¡Movimiento registrado exitosamente en la nube!", icon="🍄")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error crítico al escribir en Google Sheets: {ex}")
            else:
                st.error("❌ Por favor completa los campos obligatorios del formulario.")

    # =======================================================================
    # 📊 5. VISUALIZACIÓN DEL HISTORIAL DE MOVIMIENTOS (KARDEX)
    # =======================================================================
    st.markdown("---")
    st.markdown(f"### 📋 Historial de Transacciones - {almacen_seleccionado}")

    if not df_movs.empty:
        # Normalizar nombres de columnas por si acaso
        df_movs.columns = [c.strip() for c in df_movs.columns]
        
        # Filtrar el dataframe para mostrar únicamente los datos del almacén seleccionado
        if "Almacen" in df_movs.columns:
            df_filtrado = df_movs[df_movs["Almacen"] == almacen_seleccionado]
        else:
            df_filtrado = df_movs.copy()
            
        if not df_filtrado.empty:
            # Ordenar por fecha para ver lo más reciente primero
            if "Fecha" in df_filtrado.columns:
                df_filtrado = df_filtrado.sort_values(by="Fecha", ascending=False)
                
            # Renderizado limpio en la tabla con estilos CSS heredados de app.py
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            # Pequeño resumen de control rápido en la zona inferior
            total_ingresos = df_filtrado[df_filtrado["Tipo_Movimiento" if "Tipo_Movimiento" in df_filtrado.columns else df_filtrado.columns[3]] == "INGRESO"]["Cantidad"].sum()
            total_salidas = df_filtrado[df_filtrado["Tipo_Movimiento" if "Tipo_Movimiento" in df_filtrado.columns else df_filtrado.columns[3]] == "SALIDA"]["Cantidad"].sum()
            
            c_res1, c_res2 = st.columns(2)
            c_res1.metric(label="🟢 Total Items Ingresados", value=int(total_ingresos))
            c_res2.metric(label="🔴 Total Items Despachados", value=int(total_salidas))
        else:
            st.info(f"No se registran movimientos vigentes para el {almacen_seleccionado} hasta el momento.")
    else:
        st.info("La tabla de movimientos de la base de datos se encuentra vacía.")
