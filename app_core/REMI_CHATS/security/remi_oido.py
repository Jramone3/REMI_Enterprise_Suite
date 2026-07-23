import speech_recognition as sr
import sys

def escuchar_custodio():
    # Inicializar el reconocedor
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print(">>> ESCUCHANDO AL CUSTODIO...")
        # Ajustar para el ruido ambiente
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        # Convertir audio a texto (usa Google Speech Recognition por defecto)
        texto = r.recognize_google(audio, language="es-ES")
        print(f"CUSTODIO DIJO: {texto}")
        # Retornar el texto para que la interfaz lo reciba
        return texto
    except sr.UnknownValueError:
        print("REMI: No pude entender el audio.")
        return ""
    except sr.RequestError as e:
        print(f"REMI: Error en el servicio de voz; {e}")
        return ""

if __name__ == "__main__":
    escuchar_custodio()
