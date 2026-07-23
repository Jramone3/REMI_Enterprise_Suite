from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

ruta = "os.path.expanduser("~/") + REMI/assets/remi_fondo.png"
os.makedirs(os.path.dirname(ruta), exist_ok=True)

imagen = Image.new("RGB", (800, 600), color="black")
dibujo = ImageDraw.Draw(imagen)

fuente = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
texto = "REMI está contigo 🌿"
dibujo.text((20, 280), texto, font=fuente, fill="white")

imagen.save(ruta)
print("✅ Imagen generada:", ruta)

# Aplicar fondo en todos los escritorios
for i in range(6):
    for prop, val, tipo in [
        (f"/backdrop/screen0/monitorVGA-1/workspace{i}/image-path", ruta, "string"),
        (f"/backdrop/screen0/monitorVGA-1/workspace{i}/image-style", "3", "int")
    ]:
        try:
            subprocess.run([
                "xfconf-query", "-c", "xfce4-desktop",
                "-p", prop, "--create", "-t", tipo, "-s", val
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout en propiedad: {prop}")

# Reiniciar xfdesktop sin bloquear
try:
    subprocess.run(["pkill", "-f", "xfdesktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(["nohup", "xfdesktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ xfdesktop reiniciado sin bloqueo.")
except Exception as e:
    print("⚠️ Error reiniciando xfdesktop:", e)
