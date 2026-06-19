def guardar_foto_drive(archivo, almacen, usuario):
    """
    Sube el archivo físico directamente a la raíz de tu Google Drive 
    utilizando las credenciales de GCP existentes, evitando el límite de 50k caracteres de Sheets.
    """
    try:
        # 1. Conectar con el cliente central
        # Configuración de los permisos necesarios
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        else:
            creds_dict = dict(st.secrets)
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        # Importación interna de la librería nativa de Google Drive integrada en tu entorno
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        import io
        
        drive_service = build('drive', 'v3', credentials=creds)
        
        # 2. Configurar metadatos del archivo a subir
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nombre_archivo = f"Inspeccion_{almacen.replace(' ', '_')}_{fecha_str}.jpg"
        
        file_metadata = {'name': nombre_archivo}
        
        # Preparar los bytes binarios de la imagen de Streamlit
        bytes_data = archivo.getvalue()
        fh = io.BytesIO(bytes_data)
        formato_imagen = archivo.type if hasattr(archivo, 'type') else "image/jpeg"
        
        media = MediaIoBaseUpload(fh, mimetype=formato_imagen, resumable=True)
        
        # 3. Ejecutar la subida física al Drive del proyecto
        archivo_subido = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = archivo_subido.get('id')
        
        # 4. Cambiar permisos del archivo a "Cualquiera con el enlace puede verlo" para que cargue en la app
        user_permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        drive_service.permissions().create(
            fileId=file_id,
            body=user_permission
        ).execute()
        
        # Conseguir el link directo público para renderizar imágenes
        enlace_directo = f"https://lh3.googleusercontent.com/u/0/d/{file_id}"
        
        # 5. Registrar el enlace limpio en la pestaña 'fotos' de Google Sheets
        sh = conectar_sheets()
        if not sh: return None
        
        lista_hojas = [h.title for h in sh.worksheets()]
        if "fotos" not in lista_hojas:
            ws_fotos = sh.add_worksheet(title="fotos", rows="1000", cols="4")
            ws_fotos.append_row(["Fecha", "Almacen", "Usuario", "Enlace"])
        else:
            ws_fotos = sh.worksheet("fotos")
            
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws_fotos.append_row([fecha_registro, almacen, usuario, enlace_directo])
        
        return enlace_directo
        
    except Exception as e:
        st.error(f"Error al subir archivo a la nube e indexar: {e}")
        return None
