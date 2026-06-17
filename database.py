import streamlit as st
import pandas as pd
import database as db

# 🎯 IMPORTACIÓN COMPATIBLE DE ESTILOS (Soporta rutas absolutas y relativas del servidor)
try:
    from modulos import estilos
except ModuleNotFoundError:
    import estilos

def render(sh):
    # 🌎 1. Selector Global de Idioma en la barra lateral
    if "idioma" not in st.session_state:
        st.session_state.idioma = "es"
        
    idioma_sel = st.sidebar.selectbox("🌐 Language / 語言", ["Español", "繁體中文 (Chino Tradicional)"])
    st.session_state.idioma = "es" if "Español" in idioma_sel else "zh"
    
    # Consumir el diccionario del archivo estilos.py externo
    lang = estilos.obtener_traducciones()[st.session_state.idioma]
    
    # 🎨 2. Aplicar estilos visuales y cabecera corporativa externa
    estilos.aplicar_estilos_y_cabecera(st.session_state.idioma)
    
    st.markdown("---")
    
    # 🔐 3. Control de Permisos por Usuario
    usuario_actual = st.session_state.get("username", "Invitado")
    tiene_permiso_crud = usuario_actual in ["Larry Frank", "Supervisor Almacen", "Admin"]

    # 📊 4. Carga segura del catálogo maestro desde la nube
    try:
        ws_maestro = sh.worksheet("maestro")
        df_maestro = pd.DataFrame(ws_maestro.get_all_records())
    except Exception as e:
        st.error(f"❌ Error al conectar con el maestro: {e}")
        return

    if df_maestro.empty:
        st.warning("⚠️ El catálogo maestro de materiales está vacío.")
        return

    # Buscador interactivo bilingüe
    busqueda = st.text_input(f"🔍 {lang['buscar']}", "")
    if busqueda:
        df_filtrado = df_maestro[df_maestro['Material'].astype(str).str.contains(busqueda, case=False) | 
                                 df_maestro['Código'].astype(str).str.contains(busqueda, case=False)]
    else:
        df_filtrado = df_maestro

    # Banner informativo estético
    st.markdown("""
        <div style='background-color:#ffeeba; padding:10px; border-radius:5px; border-left:6px solid #ffc107; margin-bottom:15px; color: #856404;'>
            ⚙️ <strong>Aviso / 💡 提示:</strong> Los cambios en esta sección alteran directamente la base de datos maestra del proyecto.
        </div>
    """, unsafe_allow_html=True)

    # 🎯 5. Grilla interactiva CRUD
    col_h1, col_h2, col_h3, col_h4 = st.columns([1.5, 3, 1.5, 2.5])
    col_h1.markdown(f"**{lang['tabla_codigo']}**")
    col_h2.markdown(f"**{lang['tabla_material']}**")
    col_h3.markdown(f"**{lang['tabla_unidad']}**")
    col_h4.markdown(f"**{lang['tabla_acciones']}**")
    st.markdown("<hr style='margin:5px 0px;' />", unsafe_allow_html=True)

    for index, fila in df_filtrado.iterrows():
        c_cod, c_mat, c_uni, c_acc = st.columns([1.5, 3, 1.5, 2.5])
        
        c_cod.text(fila['Código'])
        c_mat.text(fila['Material'])
        c_uni.text(fila['Unidad'])
        
        with c_acc:
            col_b1, col_b2 = st.columns(2)
            
            # --- Acción: Modificar ---
            if col_b1.button(lang['btn_modificar'], key=f"edit_{fila['Código']}"):
                if not tiene_permiso_crud:
                    st.error(lang['error_permiso'])
                else:
                    st.session_state[f"modal_edit_{fila['Código']}"] = True

            # --- Acción: Eliminar ---
            if col_b2.button(lang['btn_eliminar'], key=f"del_{fila['Código']}"):
                if not tiene_permiso_crud:
                    st.error(lang['error_permiso'])
                else:
                    st.session_state[f"modal_del_{fila['Código']}"] = True

        # Formulario expandible para EDITAR recurso
        if st.session_state.get(f"modal_edit_{fila['Código']}", False):
            with st.expander(f"📝 Modificar Recurso: {fila['Código']}", expanded=True):
                nuevo_nom = st.text_input("Nuevo Nombre del Material:", value=fila['Material'], key=f"txt_n_{fila['Código']}")
                nueva_uni = st.text_input("Nueva Unidad de Medida:", value=fila['Unidad'], key=f"txt_u_{fila['Código']}")
                
                c_mod1, c_mod2 = st.columns(2)
                if c_mod1.button("💾 Guardar", key=f"save_{fila['Código']}"):
                    exito, msg = db.modificar_material_maestro(fila['Código'], nuevo_nom, nueva_uni)
                    if exito:
                        st.success(msg)
                        del st.session_state[f"modal_edit_{fila['Código']}"]
                        st.rerun()
                if c_mod2.button("❌ Cancelar", key=f"canc_e_{fila['Código']}"):
                    del st.session_state[f"modal_edit_{fila['Código']}"]
                    st.rerun()

        # Formulario de confirmación para ELIMINAR recurso
        if st.session_state.get(f"modal_del_{fila['Código']}", False):
            with st.error(f"⚠️ {lang['confirmar_eliminar']}: {fila['Material']} ({fila['Código']})"):
                c_del1, c_del2 = st.columns(2)
                if c_del1.button("🔥 Sí, Eliminar", key=f"conf_del_{fila['Código']}"):
                    exito, msg = db.eliminar_material_maestro(fila['Código'])
                    if exito:
                        st.success(lang['exito_eliminar'])
                        del st.session_state[f"modal_del_{fila['Código']}"]
                        st.rerun()
                    else:
                        st.error(msg)
                if c_del2.button("Cancelar", key=f"canc_d_{fila['Código']}"):
                    del st.session_state[f"modal_del_{fila['Código']}"]
                    st.rerun()
        
        st.markdown("<hr style='margin:2px 0px; border-top: 1px dashed #ddd;' />", unsafe_allow_html=True)
