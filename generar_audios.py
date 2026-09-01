from gtts import gTTS

# Audio en Español
texto_es = "Saludos Custodio. Nodo operativo sincronizado correctamente. Operando en modo bilingüe y sin fugas de datos."
tts_es = gTTS(text=texto_es, lang='es', slow=False)
tts_es.save("static/remi_saludo_es.mp3")

# Audio en Inglés
texto_en = "Greetings Custodian. Operational node synchronized successfully. Operating in bilingual mode without data leaks."
tts_en = gTTS(text=texto_en, lang='en', slow=False)
tts_en.save("static/remi_saludo_en.mp3")

print("¡Audios oficiales de Remi generados con éxito en la carpeta static/!")
