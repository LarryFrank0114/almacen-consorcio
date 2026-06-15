import streamlit as st
import database as db
import auth

# Configuración base de la página web
st.set_page_config(page_title="Consorcio San Miguel", page_icon="🏗️", layout="wide")

# Inicializar Base de Datos y Sesión de Usuario
db.inicializar_db()
auth.verificar_sesion()

if not st.session_state.logged_in:
    auth.login_form()
else:
    # --- MENÚ LATERAL ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.caption(f"Rol asignado: {st.session_state.user_role}")
        st.markdown("---")
        opcion = st.radio("📌 OPERACIONES CRUD", ["📖 Ver Inventario (Read)", "➕ Registrar Material (Create)", "✏️ Modificar Stock/Ubicación (Update)", "❌ Eliminar Material (Delete)"])
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DESARROLLO DE LAS OPCIONES CRUD ---
    
    # 1. READ (Lectura de stock en vivo)
    if opcion == "📖 Ver Inventario (Read)":
        st.markdown("## 📊 Stock en Vivo - Almacenes 6, 8 y 10")
        st.markdown("---")
        buscar = st.text_input("🔍 Buscar por descripción o código:")
        df = st.session_state.inventario
        if buscar:
            df = df[df['Material'].str.contains(buscar, case=False) | df['Código'].str.contains(buscar, case=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    # 2. CREATE (Insertar nuevos materiales a la base de datos)
    elif opcion == "➕ Registrar Material (Create)":
        st.markdown("## ➕ Agregar Nuevo Recurso al Maestro")
        st.markdown("---")
        if st.session_state.user_role != "Administrador":
            st.warning("🔒 Operación restringida. Solo el Administrador puede agregar nuevos códigos.")
        else:
            with st.form("Create Form"):
                c1, c2 = st.columns(2)
                with c1:
                    cod = st.text_input("Código Único (Ej: VAL-CO-06)").upper().strip()
                    mat = st.text_input("Descripción Completa del Material")
                    alm = st.selectbox("Asignar a Almacén:", ["Almacén 6", "Almacén 8", "Almacén 10"])
                with c2:
                    ubc = st.text_input("Ubicación de Slotting (Ej: Estante B - Nivel 1)")
                    stk = st.number_input("Stock Inicial", min_value=0, step=1)
                    uni = st.text_input("Unidad de Medida (Ej: Unidades, Metros)")
                
                encargados_dict = {"Almacén 6": "Juan Carlos R.", "Almacén 8": "Carlos M.", "Almacén 10": "Luis A."}
                enc = encargados_dict[alm]
                
                btn_crear = st.form_submit_button("💾 Guardar en Base de Datos")
                if btn_crear:
                    if not cod or not mat:
                        st.error("❌ Los campos Código y Descripción son obligatorios.")
                    else:
                        exito, msg = db.crear_registro(cod, mat, alm, ubc, stk, uni, enc)
                        if exito: st.success(msg)
                        else: st.error(msg)

    # 3. UPDATE (Modificar campos o stock de materiales existentes)
    elif opcion == "✏️ Modificar Stock/Ubicación (Update)":
        st.markdown("## ✏️ Modificar Registro de Inventario")
        st.markdown("---")
        if st.session_state.user_role != "Administrador":
            st.warning("🔒 Operación restringida. Solo el Administrador puede alterar valores físicos de stock.")
        else:
            codigos_disponibles = st.session_state.inventario['Código'].tolist()
            cod_sel = st.selectbox("Seleccione el código del material a editar:", ["-- Seleccionar --"] + codigos_disponibles)
            
            if cod_sel != "-- Seleccionar --":
                df_item = st.session_state.inventario[st.session_state.inventario['Código'] == cod_sel].iloc[0]
                st.info(f"**Material Actual:** {df_item['Material']} | **Stock Actual:** {df_item['Stock']} {df_item['Unidad']}")
                
                col_modificar = st.selectbox("¿Qué campo desea modificar?", ["Stock", "Ubicación"])
                
                if col_modificar == "Stock":
                    nuevo_val = st.number_input("Ingrese el Nuevo Stock Físico:", min_value=0, value=int(df_item['Stock']), step=1)
                else:
                    nuevo_val = st.text_input("Ingrese la Nueva Ubicación:", value=df_item['Ubicación'])
                
                if st.button("💾 Aplicar Cambio en Vivo"):
                    if db.actualizar_registro(cod_sel, col_modificar, nuevo_val):
                        st.success(f"✔️ {col_modificar} actualizado correctamente para el código {cod_sel}.")
                    else:
                        st.error("❌ Error al procesar el cambio.")

    # 4. DELETE (Eliminar materiales del inventario)
    elif opcion == "❌ Eliminar Material (Delete)":
        st.markdown("## ❌ Eliminar Ítem del Inventario")
        st.markdown("---")
        if st.session_state.user_role != "Administrador":
            st.warning("🔒 Operación restringida. Solo el Administrador puede dar de baja materiales.")
        else:
            codigos_disponibles = st.session_state.inventario['Código'].tolist()
            cod_eliminar = st.selectbox("Seleccione el código del material que desea eliminar por completo:", ["-- Seleccionar --"] + codigos_disponibles)
            
            if cod_eliminar != "-- Seleccionar --":
                df_item = st.session_state.inventario[st.session_state.inventario['Código'] == cod_eliminar].iloc[0]
                st.danger(f"⚠️ **ATENCIÓN:** Está a punto de borrar permanentemente: **{df_item['Material']}** de {df_item['Almacén']}.")
                
                confirma_eliminar = st.checkbox("Confirmo que deseo eliminar este material del sistema de forma permanente.")
                if st.button("🗑️ Confirmar Eliminación"):
                    if confirma_eliminar:
                        db.eliminar_registro(cod_eliminar)
                        st.success(f"🗑️ El código {cod_eliminar} ha sido borrado de la base de datos con éxito.")
                    else:
                        st.error("❌ Debe marcar la casilla de confirmación antes de eliminar.")
