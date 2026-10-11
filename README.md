# 🤖 REMI Enterprise Suite v1.0.0

> **Inteligencia Artificial Soberana, Segura y 100% Local para tu Empresa**

Despliega agentes autónomos y herramientas de auditoría en tu propia infraestructura (**Windows, macOS y Linux**) sin pagar tarifas por token ni arriesgar la confidencialidad de tus datos corporativos.

---

## 🏛️ ¿Por qué REMI Enterprise?

En sectores donde la confidencialidad es ley, los datos no pueden viajar a nubes públicas. REMI resuelve los tres grandes dolores del software empresarial moderno:
* 🔒 **100% On-Premise:** Procesamiento local sin fugas de datos ni telemetría externa.
* 📉 **Reducción del 70% en Costos:** Adiós a las tarifas por token de APIs de terceros.
* ⚡ **Autonomía 24/7:** Operatividad continua incluso sin conexión a Internet constante.

---

## 🛠️ Arquitectura de Doble Despliegue

La suite está estructurada para un entorno corporativo robusto:
1. **Vercel (Landing & Portal SaaS):** Presentación comercial, especificaciones de hardware, documentación y pasarela de verificación de licencias.
2. **Render & Linux Local (Comando Central / FastAPI):** Núcleo de agentes y procesamiento con Gemini Flash 2.5 integrado de forma segura contra el **Búnker MongoDB Atlas**.

---

## 📦 Despliegue Rápido (Plug & Play)

Para levantar el núcleo de comandos localmente en tu entorno Linux (`sda7` u otros):

```bash
# Clonar o desplegar el paquete firmado
git clone [https://github.com/Jramone3/REMI_Enterprise_Suite.git](https://github.com/Jramone3/REMI_Enterprise_Suite.git)
cd REMI_Enterprise_Suite

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el Centro de Comando Streamlit
streamlit run app.py

🔑 Validación y Licenciamiento Búnker
El sistema valida licencias empresariales en tiempo real conectándose de forma segura a MongoDB Atlas (remi_admin), asegurando la trazabilidad mediante contratos EOA en la Red Base.

Desarrollado por: jramonrivasg (remi.bunker.sys)

Espejo Oficial: SourceForge Mirror
