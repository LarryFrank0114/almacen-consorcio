# email_service.py - Versión simplificada sin SendGrid si no está configurado
import streamlit as st
import random
import string
import bcrypt
import jwt
import time
import os

class EmailService:
    def __init__(self):
        self.email_enabled = False
        self.jwt_secret = 'clave_secreta_predeterminada_para_desarrollo'
        
        # Intentar configurar SendGrid
        try:
            if 'sendgrid' in st.secrets:
                self.sendgrid_api_key = st.secrets['sendgrid']['api_key']
                self.from_email = st.secrets.get('secrets', {}).get('email_from', 'no-reply@almacen.com')
                self.jwt_secret = st.secrets.get('secrets', {}).get('jwt_secret_key', self.jwt_secret)
                self.email_enabled = True
            else:
                from dotenv import load_dotenv
                load_dotenv()
                self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
                self.from_email = os.getenv('EMAIL_FROM', 'no-reply@almacen.com')
                self.jwt_secret = os.getenv('JWT_SECRET_KEY', self.jwt_secret)
                self.email_enabled = bool(self.sendgrid_api_key)
        except:
            self.email_enabled = False
        
        if not self.email_enabled:
            st.warning("⚠️ SendGrid no configurado. Los códigos se mostrarán en pantalla.")
    
    def generate_verification_code(self):
        """Genera un código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_verification_email(self, to_email, verification_code):
        """Envía el código de verificación por correo (o lo muestra en pantalla)"""
        if not self.email_enabled:
            st.info(f"📧 Código de verificación para {to_email}: **{verification_code}**")
            return True
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            subject = f"Código de Verificación - Almacen Consorcio"
            html_content = f"""
            <h1>🔐 Verificación de Correo</h1>
            <p>Tu código de verificación es:</p>
            <h2 style="font-size: 32px; color: #4CAF50; letter-spacing: 5px;">{verification_code}</h2>
            <p>Este código expira en 10 minutos.</p>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            return response.status_code == 202
            
        except Exception as e:
            st.info(f"📧 Código de verificación para {to_email}: **{verification_code}**")
            return False
    
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
