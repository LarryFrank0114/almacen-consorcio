# email_service.py
import os
import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import bcrypt
import jwt
import time

load_dotenv()

class EmailService:
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.from_email = os.getenv('EMAIL_FROM')
        self.jwt_secret = os.getenv('JWT_SECRET_KEY')
    
    def generate_verification_code(self):
        """Genera un código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    def generate_verification_token(self, email):
        """Genera un token JWT para verificación de correo"""
        payload = {
            'email': email,
            'exp': time.time() + 3600  # Expira en 1 hora
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
        subject = f"Código de Verificación - {os.getenv('APP_NAME', 'Almacen Consorcio')}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #4CAF50;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                    text-align: center;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Verificación de Correo</h1>
                    <p>¡Bienvenido/a a {os.getenv('APP_NAME', 'Almacen Consorcio')}!</p>
                </div>
                
                <p>Hola,</p>
                <p>Has solicitado crear una cuenta en nuestro sistema. Para completar el registro, por favor ingresa el siguiente código de verificación:</p>
                
                <div class="code">
                    {verification_code}
                </div>
                
                <p><strong>Este código expirará en 10 minutos.</strong></p>
                <p>Si no solicitaste este registro, puedes ignorar este correo.</p>
                
                <div class="footer">
                    <p>© 2024 {os.getenv('APP_NAME', 'Almacen Consorcio')}. Todos los derechos reservados.</p>
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
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
        
        try:
            response = self.sendgrid_client.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False
    
    def hash_password(self, password):
        """Encripta una contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
