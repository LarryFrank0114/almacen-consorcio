# email_service.py
import streamlit as st
import random
import string
import bcrypt
import jwt
import time
import os
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        # Intentar obtener secrets de Streamlit Cloud
        try:
            if 'sendgrid' in st.secrets:
                self.sendgrid_api_key = st.secrets['sendgrid']['api_key']
                self.from_email = st.secrets.get('secrets', {}).get('email_from', 'no-reply@almacen.com')
                self.jwt_secret = st.secrets.get('secrets', {}).get('jwt_secret_key', 'clave_secreta_predeterminada')
            else:
                # Fallback para desarrollo local
                from dotenv import load_dotenv
                load_dotenv()
                self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
                self.from_email = os.getenv('EMAIL_FROM', 'no-reply@almacen.com')
                self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'clave_secreta_predeterminada')
        except:
            self.sendgrid_api_key = None
            self.from_email = 'no-reply@almacen.com'
            self.jwt_secret = 'clave_secreta_predeterminada'
        
        self.email_enabled = self.sendgrid_api_key and self.sendgrid_api_key != 'TU_API_KEY_AQUI'
        
        if not self.email_enabled:
            st.warning("⚠️ SendGrid no configurado. Los códigos se mostrarán en pantalla.")
    
    def generate_verification_code(self):
        """Genera un código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    def generate_verification_token(self, email):
        """Genera un token JWT para verificación de correo"""
        payload = {
            'email': email,
            'exp': time.time() + 3600
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token):
        """Verifica el token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload.get('email')
        except:
            return None
    
    def send_verification_email(self, to_email, verification_code):
        """Envía el código de verificación por correo"""
        if not self.email_enabled:
            st.info(f"📧 Código de verificación para {to_email}: **{verification_code}**")
            return True
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            subject = f"Código de Verificación - {st.secrets.get('secrets', {}).get('app_name', 'Almacen Consorcio')}"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                    .code {{ font-size: 32px; font-weight: bold; color: #4CAF50; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 5px; margin: 20px 0; letter-spacing: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 Verificación de Correo</h1>
                    <p>Hola,</p>
                    <p>Has solicitado crear una cuenta. Para completar el registro, ingresa este código:</p>
                    <div class="code">{verification_code}</div>
                    <p><strong>Este código expirará en 10 minutos.</strong></p>
                </div>
            </body>
            </html>
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
            print(f"❌ Error al enviar correo: {e}")
            st.info(f"📧 Código de verificación para {to_email}: **{verification_code}**")
            return False
    
    def hash_password(self, password):
        """Encripta una contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
