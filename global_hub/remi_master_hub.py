#!/usr/bin/env python3
import os
import re
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from github import Github, Auth
from twilio.rest import Client

REPOS_DIR = os.path.expanduser("~/REMI_CORE/global_hub")
GITHUB_USER = "Jramone3"

# Configuración de Correo (SMTP)
SMTP_SERVER = os.environ.get("REMI_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("REMI_SMTP_PORT", 587))
SMTP_USER = os.environ.get("REMI_SMTP_USER", "jramonrivasg@gmail.com")
SMTP_PASSWORD = os.environ.get("REMI_SMTP_PASSWORD", "tu_contraseña_de_aplicacion")
EMAIL_TO = "remi.bunker.sys@proton.me"

# Configuración de Twilio Sandbox para WhatsApp
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "tu_account_sid")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "tu_auth_token")
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886" # Número estándar Twilio Sandbox
USER_WHATSAPP_TO = os.environ.get("USER_WHATSAPP_TO", "whatsapp:+tu_numero_personal")

SENSITIVE_PATTERNS = [
    re.compile(r"ghp_[a-zA-Z0-9]{36}"), 
    re.compile(r"sk_live_[0-9a-zA-Z]{24,}"), 
    re.compile(r"-----BEGIN (RSA|PRIVATE) KEY-----"), 
    re.compile(r"password\s*=\s*['\"].+['\"]", re.IGNORECASE)
]

def get_github_client():
    token = os.environ.get("GITHUB_BOT_TOKEN")
    if not token:
        return Github()
    return Github(auth=Auth.Token(token))

def send_email_report(subject, body):
    try:
        if not SMTP_PASSWORD or SMTP_PASSWORD == "tu_contraseña_de_aplicacion":
            print(f"[REMI Email Simulado] Asunto: {subject}")
            return

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"[REMI Email] Reporte proactivo enviado a {EMAIL_TO}.")
    except Exception as e:
        print(f"[Error enviando correo]: {e}")

def send_whatsapp_alert(message):
    try:
        if not TWILIO_ACCOUNT_SID or TWILIO_ACCOUNT_SID == "tu_account_sid":
            print(f"[REMI WhatsApp Simulado] {message}")
            return
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=USER_WHATSAPP_TO
        )
        print("[REMI WhatsApp] Alerta proactiva enviada exitosamente.")
    except Exception as e:
        print(f"[Error enviando WhatsApp]: {e}")

def sync_repos():
    print(f"[REMI Global OS] Conectando con GitHub para el usuario: {GITHUB_USER}")
    g = get_github_client()
    try:
        user = g.get_user(GITHUB_USER)
        repos = user.get_repos(type="all")
    except Exception as e:
        print(f"[Error de conexión GitHub]: {e}")
        return

    os.makedirs(REPOS_DIR, exist_ok=True)

    for repo in repos:
        repo_name = repo.name
        clone_url = repo.clone_url
        repo_path = os.path.join(REPOS_DIR, repo_name)

        if os.path.isdir(os.path.join(repo_path, ".git")):
            try:
                subprocess.run(["git", "-C", repo_path, "pull"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                pass
        else:
            try:
                token = os.environ.get("GITHUB_BOT_TOKEN")
                auth_clone_url = clone_url.replace("https://", f"https://{token}@") if token else clone_url
                subprocess.run(["git", "clone", auth_clone_url, repo_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                pass
    print("[REMI Global OS] Sincronización masiva finalizada.")

def security_and_pattern_audit():
    print("\n[REMI Security Core] Escaneando repositorios...")
    issues = []
    for root, dirs, files in os.walk(REPOS_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            if file.endswith(('.png', '.jpg', '.zip', '.lock', '.pyc', '.pdf')):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for pattern in SENSITIVE_PATTERNS:
                        if pattern.search(content):
                            issues.append(os.path.relpath(file_path, REPOS_DIR))
            except Exception:
                pass

    report_subject = "🤖 REMI Core: Reporte Proactivo de Auditoría y Sincronización"
    report_body = f"""Hola Jesús,

Informe generado automáticamente por el núcleo de REMI en ramon-desktop:

- Estado de Sincronización: Completada en ~/REMI_CORE/global_hub.
- Alertas de seguridad o credenciales detectadas: {len(issues)}
"""
    if issues:
        report_body += "\nArchivos con posibles incidencias:\n" + "\n".join(issues)
    else:
        report_body += "\nTodos los repositorios se encuentran limpios y seguros."

    print(report_body)
    
    # Disparo proactivo omnicanal
    send_email_report(report_subject, report_body)
    send_whatsapp_alert(f"🤖 [REMI Proactivo] Sincronización OK. Alertas detectadas: {len(issues)}")

if __name__ == "__main__":
    sync_repos()
    security_and_pattern_audit()
