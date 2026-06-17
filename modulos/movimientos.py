import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

def render(sh):
    st.title("📦 Registro de Movimientos de Almacén")
    st.markdown("---")
    
    # 1. Cargar el catálogo maestro para los combos de selección
    try:
        ws_maestro = sh.worksheet("maestro")
        data_maestro = ws_maestro.get_all_records()
        df_maestro = pd.DataFrame(data_maestro)
    except Exception as e:
        st.error(f"Error al cargar el catálogo maestro: {e}")
        return

    if df_maestro.empty:
        st.warning("⚠️ El catálogo maestro está vacío. Por favor, agregue materiales primero.")
        return

    # 🎯 CORRECCIÓN CLAVE: Usamos 'Código' y 'Material' con la tipografía exacta de tu Excel/Sheets
    try:
        opciones_combo = df_maestro['Código'].astype(str) + " - " + df_maestro['Material'].astype(str)
    except KeyError:
        st.error("❌ Error de columnas: Verifica que tu hoja 'maestro' tenga las cabeceras exactas: 'Código' y 'Material'")
        return

    # 2. Inicializar la canasta temporal en la sesión si no existe
    if "canasta" not in st.session_state:
        st.session_state.canasta = []

    # 3. Formulario de Datos Generales del Movimiento
    st.subheader("📋 Datos Generales")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_movimiento = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso", "Devolución"])
        almacen = st.selectbox("Almacén de Destino/Origen", ["Almacén Central", "Almacén Norte", "Almacén Sur"])
    with col2:
        documento = st.text_input("Nº Documento / Guía", placeholder="EG-001 o FAC-123")
        solicitante = st.text_input("Solicitante / Receptor", placeholder="Nombre del operario")
    with col3:
        fecha_mov = st.date_input("Fecha de Registro", datetime.now())
        observaciones = st.text_area("Observaciones Adicionales", placeholder="Detalles del movimiento...")

    st.markdown("---")

    # 4. Selector de Materiales e Insumos (La Canasta)
    st.subheader("🛒 Agregar Insumos al Documento Abierto")
    col_mat, col_cant, col_btn = st.columns([5, 2, 2])

    with col_mat:
        seleccion_material = st.selectbox("Seleccione el Material", opciones_combo)
    with col_cant:
        cantidad_item = st.number_input("Cantidad", min_value=1, value=1, step=1)
    with col_btn:
        st.write("<br>", unsafe_allow_html=True) # Espaciador estético
        if st.button("➕ Añadir a Lista"):
            # Extraer el código separado por el guion
            codigo_sel = seleccion_material.split(" - ")[0]
            fila_material = df_maestro[df_maestro['Código'].astype(str) == codigo_sel].iloc[0]
            
            # Insertar a la lista temporal
            st.session_state.canasta.append({
                "Código": codigo_sel,
                "Material": fila_material['Material'],
                "Cantidad": int(cantidad_item),
                "Unidad": fila_material['Unidad']
            })
            st.toast("Material añadido a la lista", icon="✅")

    # 5. Mostrar la lista agregada y control de Fotos
    if st.session_state.canasta:
        st.markdown("### 📋 Ítems listos para procesar")
        df_canasta = pd.DataFrame(st.session_state.canasta)
        st.dataframe(df_canasta, use_container_width=True)

        if st.button("🗑️ Limpiar Lista"):
            st.session_state.canasta = []
            st.rerun()

        st.markdown("---")
        st.subheader("📸 Evidencia Fotográfica (Opcional)")
        foto_archivo = st.file_uploader("Subir foto de la guía o materiales", type=["jpg", "jpeg", "png"])

        if foto_archivo is not None:
            st.image(foto_archivo, caption="Evidencia cargada en memoria", width=300)

        # 6. Botón Final de Procesar y Guardar todo en Google Sheets
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🚀 Confirmar y Registrar Movimiento Completo"):
            usuario_activo = st.session_state.get("username", "Usuario Sistema")
            fecha_str = fecha_mov.strftime("%Y-%m-%d")

            with st.spinner("Procesando transacciones e inventario central..."):
                # Primero guardamos la foto si el usuario subió una
                if foto_archivo is not None:
                    db.guardar_foto_drive(foto_archivo, almacen, usuario_activo)

                # Registramos el lote completo en el historial e inventario
                exito, msg = db.registrar_transaccion_avanzada(
                    tipo=tipo_movimiento,
                    documento=documento,
                    almacen=almacen,
                    fecha=fecha_str,
                    solicitante=solicitante,
                    usuario=usuario_activo,
                    obs=observaciones,
                    canasta=st.session_state.canasta
                )

                if exito:
                    st.success(f"✨ {msg}")
                    st.session_state.canasta = [] # Vaciamos la lista tras el éxito
                    st.balloons()
                else:
                    st.error(f"❌ {msg}")
