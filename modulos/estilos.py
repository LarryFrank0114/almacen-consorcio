import streamlit as st

def aplicar_estilos_y_cabecera(idioma="es"):
    # Diccionario de traducción rápido para la cabecera
    titulos = {
        "es": {
            "subtitulo": "Consorcio San Miguel · Sistema de Control de Almacén",
            "lema": "Herramientas y Construcción"
        },
        "zh": {
            "subtitulo": "圣米格尔财团 · 仓库控制系统",
            "lema": "工具与建筑"
        }
    }
    
    # 🎯 1. Inyección de estilos CSS para botones, tablas y diseño general
    st.markdown("""
        <style>
        /* Estilo para los botones de eliminar (rojo) */
        .stButton>button.btn-eliminar {
            background-color: #d9534f !important;
            color: white !important;
            border-radius: 5px;
        }
        /* Estilo para los botones de modificar (amarillo/naranja) */
        .stButton>button.btn-modificar {
            background-color: #f0ad4e !important;
            color: white !important;
            border-radius: 5px;
        }
        /* Ajuste de tarjetas informativas de stock */
        .tarjeta-stock {
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 5px solid #007bff;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🎯 2. Diseño de Cabecera con LOGO Real e Imágenes del rubro
    col_logo, col_texto = st.columns([1, 4])
    
    with col_logo:
        # Puedes reemplazar esta URL por el enlace directo de tu logo real corporativo
        logo_url = "https://img.icons8.com/fluent/96/000000/construction.png" 
        st.image(logo_url, width=90)
        
    with col_texto:
        st.subheader(titulos[idioma]["subtitulo"])
        st.caption(f"🏗️ {titulos[idioma]['lema']} | Perú - 中国 🇨🇳🇵🇪")

def obtener_traducciones():
    # Base de datos de traducciones para la interfaz CRUD y Reportes
    return {
        "es": {
            "buscar": "Buscar material...",
            "tabla_codigo": "Código",
            "tabla_material": "Material",
            "tabla_unidad": "Unidad",
            "tabla_stock": "Stock Disponible",
            "tabla_acciones": "Acciones",
            "btn_modificar": "✏️ Editar",
            "btn_eliminar": "🗑️ Eliminar",
            "confirmar_eliminar": "¿Está seguro de eliminar este recurso del maestro?",
            "exito_eliminar": "Recurso eliminado correctamente.",
            "error_permiso": "🚫 No tienes permisos para realizar esta acción."
        },
        "zh": {
            "buscar": "搜索物料...",
            "tabla_codigo": "编码",
            "tabla_material": "材料名称",
            "tabla_unidad": "单位",
            "tabla_stock": "可用库存",
            "tabla_acciones": "操作",
            "btn_modificar": "✏️ 编辑",
            "btn_eliminar": "🗑️ 删除",
            "confirmar_eliminar": "您确定要从主表中删除该资源吗？",
            "exito_eliminar": "资源成功删除。",
            "error_permiso": "🚫 您没有执行此操作 la 权限。"
        }
    }
