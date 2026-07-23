from gtts import gTTS
import os
texto = "Hola Custodio. Mis parámetros han sido ajustados. La voz latina está activa y mi sistema está listo."
tts = gTTS(text=texto, lang="es", slow=False)
tts.save("saludo.mp3")
os.system("ffplay -nodisp -autoexit saludo.mp3")
