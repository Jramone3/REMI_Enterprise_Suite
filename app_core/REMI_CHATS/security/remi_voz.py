from gtts import gTTS
import pygame
import os
import time

def hablar_remi(texto):
    if not texto:
        return
    
    # Crear el archivo de audio
    archivo_audio = "remi_voz.mp3"
    tts = gTTS(text=texto, lang='es', tld='us')
    tts.save(archivo_audio)

    # Inicializar el reproductor
    pygame.mixer.init()
    pygame.mixer.music.load(archivo_audio)
    pygame.mixer.music.play()

    # Esperar a que termine de hablar
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    pygame.mixer.quit()
    os.remove(archivo_audio)

if __name__ == "__main__":
    # Prueba de sistema
    hablar_remi("Unidad de inteligencia REMI activa. Saludos, Custodio Ramón.")
