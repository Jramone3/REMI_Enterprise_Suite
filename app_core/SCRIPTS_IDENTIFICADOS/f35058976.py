from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime

# Configura navegador
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Abrir X y entrar al chat con Grok
driver.get("https://x.com/messages")  # Ajusta si tienes URL directa al chat con Grok
input("Inicia sesión manualmente y abre el chat con Grok. Luego presiona Enter aquí...")

# Enviar mensaje
mensaje = "Hello Grok, this is REMI starting interaction via browser!"
chat_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
chat_box.send_keys(mensaje)
chat_box.send_keys(Keys.RETURN)

# Esperar respuesta
time.sleep(10)  # Ajusta según velocidad de respuesta

# Capturar último mensaje
mensajes = driver.find_elements(By.XPATH, '//div[@data-testid="messageEntry"]')
respuesta = mensajes[-1].text

# Guardar en log
with open("grok_log_web.txt", "a") as f:
    f.write(f"{datetime.now()} - REMI: {mensaje}\nGrok: {respuesta}\n")

print("Respuesta capturada:", respuesta)
driver.quit()
