monto_enviado = 0.00473989
decimales = str(monto_enviado)[-4:]

print(f"🕵️‍♂️ REMI: Analizando el código de ruta de tu envío...")
print(f"🔢 Monto: {monto_enviado} ETH")
print(f"🆔 Código detectado: {decimales}")

# Códigos comunes de Orbiter (pueden variar)
rutas = {
    "9001": "Ethereum Mainnet",
    "9006": "Polygon",
    "9023": "Base",
    "9007": "Optimism"
}

if decimales in rutas:
    print(f"✅ La ruta es correcta hacia: {rutas[decimales]}")
else:
    print(f"⚠️ ATENCIÓN: El código {decimales} no es estándar.")
    print("Es posible que el bot de Orbiter no sepa a qué red enviar el dinero.")

