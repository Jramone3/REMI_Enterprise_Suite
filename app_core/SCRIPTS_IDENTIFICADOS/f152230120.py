from flask import Flask, redirect, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
@app.route('/')
def home():
    return '<a href="/login">Iniciar sesión con GitHub</a>'

@app.route('/login')
def login():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={CLIENT_ID}')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_res = requests.post('https://github.com/login/oauth/access_token', data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code
    }, headers={'Accept': 'application/json'})
    token = token_res.json().get('access_token')
    return f'Token recibido: {token}'

# Token recibido tras autenticación exitosa
TOKEN_VALIDO = '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'

@app.route('/activar_remi')
def activar_remi():
    token = request.headers.get('Authorization')
    if not token or token != f'Bearer {TOKEN_VALIDO}':
        return '❌ Acceso denegado: token inválido.', 403
    return '✅ REMI activado con autenticación validada.'

if __name__ == '__main__':
    app.run(debug=True)
