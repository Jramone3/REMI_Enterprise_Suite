from PIL import Image, ImageDraw, ImageFont
import os

ruta = "os.path.expanduser("~/") + REMI/assets/remi_fondo.png"
os.makedirs(os.path.dirname(ruta), exist_ok=True)

imagen = Image.new("RGB", (800, 600), color="black")
dibujo = ImageDraw.Draw(imagen)

# Cargar fuente con soporte Unicode
fuente = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)

# Texto con emoji
texto = "REMI está contigo 🌿"
dibujo.text((20, 280), texto, font=fuente, fill="white")

imagen.save(ruta)
print("Imagen generada correctamente:", ruta)
