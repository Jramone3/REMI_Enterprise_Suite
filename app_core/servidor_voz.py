from flask import Flask, request
from flask_cors import CORS
from gtts import gTTS
import os

app = Flask(__name__)
CORS(app)

# Esta es la ruta que tu web está buscando frenéticamente
@app.route('/api/status_caza', methods=['GET'])
def status_caza():
    return {"status": "activo", "message": "REMI está vigilando el terreno"}

@app.route('/hablar', methods=['POST'])
def hablar():
    data = request.get_json()
    texto = data.get('texto', 'Hola Custodio.')
    tts = gTTS(text=texto, lang='es', slow=False)
    tts.save("respuesta.mp3")
    os.system("ffplay -nodisp -autoexit respuesta.mp3")
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(port=5000)
