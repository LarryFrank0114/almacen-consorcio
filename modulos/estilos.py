import streamlit as st

def obtener_traducciones():
    return {
        "es": {
            "buscar": "Buscar Material...",
            "tabla_codigo": "Código",
            "tabla_material": "Material",
            "tabla_unidad": "Unidad",
            "tabla_acciones": "Acciones",
            "btn_modificar": "📝 Modificar",
            "btn_eliminar": "🗑️ Eliminar",
            "error_permiso": "❌ No tienes permisos para modificar el catálogo maestro.",
            "confirmar_eliminar": "Confirmar eliminación",
            "exito_eliminar": "Material eliminado correctamente."
        },
        "zh": {
            "buscar": "搜尋材料...",
            "tabla_codigo": "代碼",
            "tabla_material": "材料名稱",
            "tabla_unidad": "單位",
            "tabla_acciones": "操作",
            "btn_modificar": "📝 修改",
            "btn_eliminar": "🗑️ 刪除",
            "error_permiso": "❌ 您沒有修改主目錄的權限。",
            "confirmar_eliminar": "確認刪除",
            "exito_eliminar": "材料已成功刪除。"
        }
    }

def aplicar_estilos_y_cabecera(idioma):
    if idioma == "es":
        st.title("📊 Cuadro de Control Operativo")
        st.subheader("Consorcio San Miguel — Gestión de Infraestructura y Almacenes")
    else:
        st.title("📊 營運控制面板")
        st.subheader("三美工務財團 — 基礎設施與倉庫管理")
