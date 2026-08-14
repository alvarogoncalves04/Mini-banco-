# 05_automatizacion.py
import schedule
import time
from datetime import datetime
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def ejecutar_etl():
    """Ejecuta el pipeline ETL"""
    print(f"\n🚀 Ejecutando ETL a las {datetime.now()}")
    try:
        subprocess.run(["python", "src/02_etl_pipeline.py"], check=True)
        print("✅ ETL completado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error en ETL: {e}")
        return False

def enviar_reporte():
    """Envía reporte por correo después del ETL"""
    print("📧 Enviando reporte por correo...")
    
    remitente = "sistema@banco.com"
    destinatario = "oficial.cumplimiento@banco.com"
    
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = f"Reporte Automático - {datetime.now().strftime('%Y-%m-%d')}"
    
    cuerpo = f"""
    Reporte automático de monitoreo bancario.
    
    Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    ETL ejecutado correctamente.
    
    Este es un mensaje automático, por favor no responder.
    """
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    
    # Aquí iría la configuración SMTP del banco
    print("✅ Correo enviado (simulado)")

def trabajo_completo():
    """Ejecuta ETL + envía reporte"""
    if ejecutar_etl():
        enviar_reporte()

def iniciar_programador():
    """Inicia el programador de tareas"""
    print("⏰ Programador iniciado")
    print("📅 Tareas programadas:")
    print("   - 8:00 AM: ETL diario")
    print("   - 8:00 PM: ETL diario")
    
    schedule.every().day.at("08:00").do(trabajo_completo)
    schedule.every().day.at("20:00").do(trabajo_completo)
    
    # También corre al inicio para probar
    trabajo_completo()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    iniciar_programador()