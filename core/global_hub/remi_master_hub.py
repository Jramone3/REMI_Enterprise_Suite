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

# SMTP Configuration (Technical Environment Variables)
SMTP_SERVER = os.environ.get("REMI_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("REMI_SMTP_PORT", 587))
SMTP_USER = os.environ.get("REMI_SMTP_USER", "jramonrivasg@gmail.com")
SMTP_PASSWORD = os.environ.get("REMI_SMTP_PASSWORD", "tu_contraseña_de_aplicacion")
EMAIL_TO = "remi.bunker.sys@proton.me"

# Twilio Sandbox Configuration (WhatsApp Telemetry)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "tu_account_sid")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "tu_auth_token")
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio Sandbox Standard Number
USER_WHATSAPP_TO = os.environ.get("USER_WHATSAPP_TO", "whatsapp:+tu_numero_personal")

SENSITIVE_PATTERNS = [
    re.compile(r"ghp_[a-zA-Z0-9]{36}"), 
    re.compile(r"sk_live_[0-9a-zA-Z]{24,}"), 
    re.compile(r"-----BEGIN (RSA|PRIVATE) KEY-----"), 
    re.compile(r"password\s*=\s*['\"].+['\"]", re.IGNORECASE)
]

def get_github_client():
    """Initializes authenticated GitHub API client wrapper."""
    token = os.environ.get("GITHUB_BOT_TOKEN")
    if not token:
        return Github()
    return Github(auth=Auth.Token(token))

def send_email_report(subject, body):
    """Dispatches encrypted email report payload via SMTP daemon."""
    try:
        if not SMTP_PASSWORD or SMTP_PASSWORD == "tu_contraseña_de_aplicacion":
            print(f"[REMI_EMAIL_SIMULATION]: Subject: {subject}")
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
        print(f"[REMI_EMAIL_SUCCESS]: Proactive report dispatched to {EMAIL_TO}.")
    except Exception as e:
        print(f"[REMI_EMAIL_ERROR]: Dispatch exception -> {e}")

def send_whatsapp_alert(message):
    """Dispatches proactive WhatsApp notification via Twilio REST API."""
    try:
        if not TWILIO_ACCOUNT_SID or TWILIO_ACCOUNT_SID == "tu_account_sid":
            print(f"[REMI_WHATSAPP_SIMULATION]: {message}")
            return
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=USER_WHATSAPP_TO
        )
        print("[REMI_WHATSAPP_SUCCESS]: Telemetry alert dispatched successfully.")
    except Exception as e:
        print(f"[REMI_WHATSAPP_ERROR]: Telemetry dispatch exception -> {e}")

def sync_repositories():
    """Executes massive synchronization of remote GitHub repositories into local hub."""
    print(f"[REMI_GLOBAL_OS]: Connecting to GitHub API for custodian: {GITHUB_USER}")
    github_client = get_github_client()
    try:
        user_instance = github_client.get_user(GITHUB_USER)
        repositories = user_instance.get_repos(type="all")
    except Exception as e:
        print(f"[REMI_GITHUB_ERROR]: Connection exception -> {e}")
        return

    os.makedirs(REPOS_DIR, exist_ok=True)

    for repo in repositories:
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
    print("[REMI_GLOBAL_OS]: Repository synchronization sequence completed.")

def run_security_audit():
    """Scans local repository tree for hardcoded secrets and credential patterns."""
    print("\n[REMI_SECURITY_CORE]: Executing repository vulnerability scan...")
    detected_issues = []
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
                            detected_issues.append(os.path.relpath(file_path, REPOS_DIR))
            except Exception:
                pass

    report_subject = "🤖 REMI Core: Proactive Security Audit & Sync Report"
    
    # LATAM SPANISH USER OUTPUT RENDER
    report_body = f"""Hola Jesús,

Informe generado automáticamente por el núcleo soberano de REMI en ramon-desktop:

- Estado de Sincronización: Completada en ~/REMI_CORE/global_hub.
- Alertas de seguridad o credenciales detectadas: {len(detected_issues)}
"""
    if detected_issues:
        report_body += "\nArchivos con posibles incidencias:\n" + "\n".join(detected_issues)
    else:
        report_body += "\nTodos los repositorios se encuentran limpios y seguros."

    print(report_body)
    
    # Omnichannel Telemetry Dispatch
    send_email_report(report_subject, report_body)
    send_whatsapp_alert(f"🤖 [REMI Proactivo] Sincronización OK. Alertas detectadas: {len(detected_issues)}")

if __name__ == "__main__":
    sync_repositories()
    run_security_audit()
