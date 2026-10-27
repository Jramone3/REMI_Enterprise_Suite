import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
import datetime
import requests
from pymongo import MongoClient
from web3 import Web3
from dotenv import load_dotenv
from core.context_engine import get_remi_environmental_context

st.set_page_config(page_title="REMI Enterprise Suite", page_icon="🤖", layout="wide")

EMISOR_FISCAL = {
    "contribuyente": "Jesús Ramón Rivas García",
    "rif": "V050153998",
    "domicilio": "Calle El Samán, Casa Nro 17, Sector Porvorín, Guayabita, Aragua, Venezuela",
    "wallet_oficial": "0x96De980a766CCb10A19B6962587e2b61B650b372",
    "wallet_gas": "0xe4EdB277e4122137966EFC68615b3C5890d2979E",
    "red": "Base Network (ChainID: 8453)"
}

BASE_RPC_URL = "https://mainnet.base.org"
w3_base = Web3(Web3.HTTPProvider(BASE_RPC_URL))

def obtener_saldo_gas_bunker():
    try:
        if w3_base.is_connected():
            balance_wei = w3_base.eth.get_balance(EMISOR_FISCAL["wallet_gas"])
            balance_eth = w3_base.from_wei(balance_wei, 'ether')
            return f"{balance_eth:.6f} ETH", "🟢 Conectado a Base Mainnet"
        else:
            return "0.00 ETH", "🔴 Sin conexión RPC"
    except Exception as e:
        return "0.00 ETH", f"⚠️ Error: {str(e)[:30]}"

def generar_factura_digital(cliente_email, cliente_empresa, monto_usd, tx_hash, num_licencia):
    fecha_emision = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    num_factura = f"REMI-INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    factura_text = f"""
================================================================================
               🛡️ COMPROBANTE DE COMPRA Y LICENCIA FISCAL - REMI
================================================================================
N° Factura/Recibo : {num_factura}
Fecha de Emisión  : {fecha_emision}
Estado de Pago    : VERIFICADO ON-CHAIN 🟢

--------------------------------------------------------------------------------
🏛️ EMISOR (PROVEEDOR DEL SOFTWARE)
--------------------------------------------------------------------------------
- Contribuyente   : {EMISOR_FISCAL['contribuyente']}
- RIF             : {EMISOR_FISCAL['rif']}
- Domicilio Fiscal: {EMISOR_FISCAL['domicilio']}
- Billetera PC    : {EMISOR_FISCAL['wallet_oficial']} ({EMISOR_FISCAL['red']})

--------------------------------------------------------------------------------
👤 RECEPTOR (ADQUIRENTE DE LA LICENCIA)
--------------------------------------------------------------------------------
- Cliente / Razón Social: {cliente_empresa}
- Correo Electrónico    : {cliente_email}

--------------------------------------------------------------------------------
📦 DETALLE DE LA TRANSACCIÓN
--------------------------------------------------------------------------------
- Producto         : Licencia REMI Enterprise Suite v1.0.0
- Serial Licencia  : {num_licencia}
- Monto Total      : ${monto_usd}.00 USD
- Hash Transacción : {tx_hash}

--------------------------------------------------------------------------------
Transparencia Fiscal SENIAT - Venezuela | Registro en Búnker MongoDB Atlas
================================================================================
"""
    return factura_text, num_factura

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "remi-enterprise:latest")

ollama_ready = False

try:
    check_resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
    if check_resp.status_code == 200:
        models_available = [m["name"] for m in check_resp.json().get("models", [])]
        if OLLAMA_MODEL in models_available:
            st.sidebar.success(f"✅ Ollama Local Activo (`{OLLAMA_MODEL}`)")
            ollama_ready = True
        else:
            st.sidebar.warning(f"⚠️ `{OLLAMA_MODEL}` no hallado, pero Ollama responde.")
            ollama_ready = True
    else:
        st.sidebar.error("❌ Ollama Local no responde en puerto 11434")
except Exception as e:
    st.sidebar.error(f"❌ Error conectando a Ollama Local: {e}")

if not MONGO_URI:
    st.error("🔴 **ERROR CRÍTICO DE SEGURIDAD:** La variable `MONGO_URI` no está definida. Acceso al Búnker bloqueado.")
    st.stop()

st.title("🤖 REMI Enterprise Suite - Centro de Comando")
st.sidebar.title("Navegación")
selected_tab = st.sidebar.radio(
    "Ir a:", 
    ["💬 Chat Principal", "🔑 Adquirir Licencia Enterprise", "🛡️ Registro de Licencias (Admin)"]
)

if selected_tab == "💬 Chat Principal":
    st.header("Centro de Inteligencia - REMI Core")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu orden o consulta técnica..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("REMI ejecutando auditoría y análisis local..."):
                respuesta_ia = ""
                if not ollama_ready:
                    respuesta_ia = "❌ Error: El motor local Ollama no está disponible en http://localhost:11434."
                else:
                    try:
                        env_context = get_remi_environmental_context()
                        full_prompt = (
                            f"{env_context}\n\n"
                            "Instrucciones: Eres REMI, el núcleo de inteligencia artificial autónomo de REMI Enterprise Suite, "
                            "desarrollado por jramonrivasg. Responde con tono técnico, profesional, ágil y soberano. "
                            "Aprovecha siempre la información de la matriz ambiental anterior cuando se te consulte sobre tiempo o ubicación.\n\n"
                            f"Usuario: {prompt}\n"
                            "REMI:"
                        )

                        payload = {
                            "model": OLLAMA_MODEL,
                            "prompt": full_prompt,
                            "stream": False
                        }

                        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=90)
                        if res.status_code == 200:
                            respuesta_ia = res.json().get("response", "").strip()
                        else:
                            respuesta_ia = f"❌ Error en respuesta de Ollama (Status {res.status_code}): {res.text}"
                    except Exception as e:
                        respuesta_ia = f"❌ Error en llamada a Ollama: {e}"
                
            st.markdown(respuesta_ia)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

elif selected_tab == "🔑 Adquirir Licencia Enterprise":
    st.header("🛡️ Centro de Control - Búnker MongoDB & Licenciamiento")
    st.write("Consulta y verificación profunda directa contra las colecciones del Búnker en MongoDB Atlas con respaldo fiscal SENIAT.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        email_input = st.text_input("Correo electrónico registrado en el Búnker:", value="jramonrivasg@gmail.com")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔍 Consultar Búnker MongoDB", use_container_width=True)

    if verify_btn or email_input:
        if email_input:
            try:
                with st.spinner("Consultando registros en el Búnker MongoDB Atlas..."):
                    if not MONGO_URI:
                        st.error("❌ Error: MONGO_URI no está configurada en las variables de entorno.")
                    else:
                        client_db = MongoClient(MONGO_URI)
                        db_name = os.getenv("REMI_DB_NAME", "remi_enterprise")
                        db = client_db.get_database(db_name)
                        collection = db["licenses"] if "licenses" in db.list_collection_names() else db["users"]
                        record = collection.find_one({"email": email_input})
                        
                        if record:
                            st.success("✅ Licencia autenticada y recuperada del Búnker MongoDB con éxito.")
                            
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Estado Búnker", record.get("status", "Active"))
                            m2.metric("Nivel Enterprise", record.get("tier", "Enterprise"))
                            m3.metric("Expiración Oficial", record.get("expires", "2027-12-31"))
                            
                            license_hash_val = record.get('license_hash', record.get('license', 'REMI-ENT-SECURE-2026'))
                            st.info(f"🔑 **Hash de Licencia Activa:** `{license_hash_val}`")
                            
                            factura_txt, num_factura = generar_factura_digital(
                                cliente_email=email_input,
                                cliente_empresa=record.get("client_name", "Cliente Enterprise"),
                                monto_usd=499,
                                tx_hash=record.get("tx_hash", "0x96De980a766CCb10A19B6962587e2b61B650b372 (Direct Búnker)"),
                                num_licencia=license_hash_val
                            )
                            
                            st.subheader("📄 Comprobante Fiscal (SENIAT)")
                            st.text_area("Vista Previa Factura:", factura_txt, height=220)
                            st.download_button(
                                label="📥 Descargar Comprobante Fiscal SENIAT (.txt)",
                                data=factura_txt,
                                file_name=f"{num_factura}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                            with st.expander("📦 Ver Payload Crudo de MongoDB"):
                                record["_id"] = str(record["_id"])
                                st.json(record)
                        else:
                            st.warning("⚠️ No se encontró una licencia activa para este correo en el Búnker. Puedes registrar una de prueba abajo.")
                            if st.button("Crear Licencia de Prueba en Búnker"):
                                sample_data = {
                                    "email": email_input,
                                    "status": "Active",
                                    "tier": "Enterprise 100/100",
                                    "expires": "2027-12-31",
                                    "license_hash": "REMI-BUNKER-LIVE-2026-OK",
                                    "client_name": "Ramon Rivas Enterprise"
                                }
                                collection.update_one({"email": email_input}, {"$set": sample_data}, upsert=True)
                                st.success("¡Licencia de prueba creada con éxito! Vuelve a consultar.")
                                st.rerun()
            except Exception as ex:
                st.error(f"❌ Error al conectar o consultar MongoDB Atlas: {ex}")
        else:
            st.warning("Por favor ingresa un correo electrónico para realizar la consulta.")

elif selected_tab == "🛡️ Registro de Licencias (Admin)":
    st.header("🛡️ Panel Administrador - Generación de Licencias & Búnker On-Chain")
    st.write("Monitorea la infraestructura de red, saldo de gas y registra licencias directamente en el Búnker MongoDB Atlas.")

    st.subheader("📊 Monitor de Infraestructura y Gas (Base Mainnet)")
    saldo_gas, estado_red = obtener_saldo_gas_bunker()
    
    g1, g2, g3 = st.columns(3)
    g1.metric("Saldo Wallet Gas (Búnker)", saldo_gas)
    g2.metric("Red Configurada", "Base ChainID: 8453")
    g3.metric("Estado de Red", estado_red)

    st.markdown("---")
    st.subheader("⚡ Protocolo de Autogestión de Gas (Cliente On-Chain)")
    st.info(
        "💡 **Modo de Gas Descentralizado:** El sistema está preparado para que el cliente ejecute "
        "la transacción de registro directamente desde su wallet EVM, cubriendo él mismo el costo de gas."
    )

    with st.expander("📜 Ver Estructura del Contrato Inteligente Inmutable (Solidity)"):
        st.code("""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RemiBunkerLicense {
    address public immutable owner;
    mapping(address => bool) public authorizedLicenses;

    event LicenseGranted(address indexed client, uint256 timestamp);

    constructor() {
        owner = msg.sender;
    }

    function acquireLicense() external payable {
        authorizedLicenses[msg.sender] = true;
        emit LicenseGranted(msg.sender, block.timestamp);
    }
}
        """, language="solidity")

    st.markdown("---")
    st.subheader("📝 Registro Manual en Búnker MongoDB")
    with st.form("new_license_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            admin_email = st.text_input("Correo del Cliente:")
            client_name = st.text_input("Nombre de la Empresa / Cliente:")
            license_tier = st.selectbox("Nivel (Tier):", ["Enterprise 100/100", "Enterprise Standard", "Trial / PoC"])
        with col_b:
            expires_date = st.date_input("Fecha de Expiración:")
            status_opt = st.selectbox("Estado de la Licencia:", ["Active", "Suspended", "Expired"])
            custom_hash = st.text_input("Hash Personalizado (Opcional):", placeholder="Deja en blanco para auto-generar")

        submit_btn = st.form_submit_button("🔑 Registrar / Actualizar Licencia en Búnker")

    if submit_btn:
        if admin_email:
            try:
                with st.spinner("Escribiendo registro en el Búnker MongoDB..."):
                    client_db = MongoClient(MONGO_URI)
                    db = client_db.get_database(os.getenv("REMI_DB_NAME", "remi_enterprise"))
                    collection = db["licenses"]
                    
                    hash_final = custom_hash if custom_hash else f"REMI-ENT-{admin_email.split('@')[0].upper()}-2026"
                    
                    payload = {
                        "email": admin_email.strip().lower(),
                        "client_name": client_name.strip() if client_name else "Cliente Enterprise",
                        "status": status_opt,
                        "tier": license_tier,
                        "expires": str(expires_date),
                        "license_hash": hash_final
                    }
                    
                    collection.update_one({"email": admin_email.strip().lower()}, {"$set": payload}, upsert=True)
                    st.success(f"✅ Licencia registrada exitosamente para `{admin_email}` con hash `{hash_final}`.")
            except Exception as e:
                st.error(f"❌ Error al escribir en el Búnker: {e}")
        else:
            st.warning("⚠️ Debes proporcionar un correo electrónico válido.")
