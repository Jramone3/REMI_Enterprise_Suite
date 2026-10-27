from gtts import gTTS
import os
import sys

texto = " ".join(sys.argv[1:])
# slow=False hace que sea mucho más rápida de forma nativa
tts = gTTS(text=texto, lang='es', slow=False)
tts.save("vega.mp3")

# Usamos ffmpeg para acelerar el audio un 20% (atempo=1.2) sin cambiar el tono
os.system("ffmpeg -i vega.mp3 -filter:a 'atempo=1.2' -y vega_rapida.mp3 > /dev/null 2>&1")
os.system("mpg123 -q vega_rapida.mp3")
