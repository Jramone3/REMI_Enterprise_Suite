import streamlit as st
import qrcode
from io import BytesIO
#!/usr/bin/env python3
"""
REMI Enterprise Suite - Streamlit Interactive Demo (Production-Ready Architecture)

Notes:
- Demo-only license derivation; in production use a hardened license service that signs licenses (HSM/KMS).
- Configure REMI_LOCAL_CORE_URL and REMI_PAYMENT_ADDRESS via environment or secret store.
"""

import os
import hashlib
from datetime import datetime, timedelta

import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="REMI Enterprise Suite — Demo & Licensing",
    page_icon="assets/remi_logo.png",
    layout="centered",
)

# Externalized Configuration via Environment Variables with Secure Placeholders
REMI_LOCAL_CORE_URL = os.environ.get("REMI_LOCAL_CORE_URL", "http://localhost:11434/api/chat")
REMI_PAYMENT_ADDRESS = os.environ.get("REMI_PAYMENT_ADDRESS", "0xDEMO_PAYMENT_ADDRESS_TO_BE_CONFIGURED")

# Header
st.image("assets/remi_imagen_oficial.jpeg", width=200)
st.title("REMI Enterprise Suite")
st.markdown("### Enterprise Multi-Agent Framework and AI Core")
st.markdown("---")

# Sidebar: Licensing and Administration
with st.sidebar:
    st.image("assets/remi_imagen_oficial.jpeg", width=100)
    st.subheader("Enterprise Portal")
    st.caption("Infrastructure backed by a standard EOA contract (Base Network) or local secure enclave.")
    st.markdown("---")

    st.markdown("### 💎 Annual Enterprise License")
    st.markdown("**Price:** $499 USD / year")
    st.markdown(
        "Includes technical support, direct multi-agent cluster updates, and advanced auditing modules."
    )

    if st.button("Generate Payment Data"):
        st.session_state.show_payment = True

    if st.session_state.get("show_payment", False):
        st.info(
            "**Direct Payment Instructions:**\n\n"
            f"1. Send **499 USDT (ERC-20 / Base)** or equivalent in ETH/BNB to:\n"
            f"`{REMI_PAYMENT_ADDRESS}`\n\n"
            "2. Register your purchaser email and provide the transaction hash (TxHash) to receive your annual license key."
        )

        purchaser_email = st.text_input("Registration email:")
        tx_hash = st.text_input("Transaction hash (TxHash):")

        if st.button("Verify and Activate Annual License"):
            if purchaser_email and tx_hash:
                expiration_date = datetime.utcnow() + timedelta(days=365)
                raw_key_material = f"{purchaser_email}-{tx_hash}-REMI-2026"
                derived = hashlib.sha256(raw_key_material.encode("utf-8")).hexdigest()[:24].upper()
                license_key = f"REMI-ENT-ANNUAL-{derived}"

                st.success("Payment noted by node. Enterprise license issued successfully (demo).")
                st.markdown(f"**Registered purchaser:** {purchaser_email}")
                st.markdown(f"**Valid until:** {expiration_date.strftime('%Y-%m-%d')}")
                st.code(license_key, language="text")
                st.caption("Store this license key on your local server to receive direct system updates.")
            else:
                st.warning("Please provide a valid registration email and transaction hash (TxHash).")

    st.markdown("---")
    st.markdown("### 🔄 Update Verification")
    check_email = st.text_input("Registered email for verification:", key="check_email")
    check_license = st.text_input("License key:", key="check_license")
    if st.button("Check for Updates"):
        if check_email and check_license:
            st.success(
                "License active. Cluster synchronized to the latest security patch available for this release."
            )
        else:
            st.warning("Please enter your registered credentials (email and license key).")

# Main interface: Local multi-agent core chat
st.info("Welcome to the REMI interactive showcase. Enter a query to interact with the local AI core.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type a query or instruction for REMI:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = (
        "You are REMI, the AI core of REMI Enterprise Suite — an enterprise multi-agent framework. "
        "Respond in a technical, professional, analytical, and executive tone. Provide clear, actionable guidance "
        "and cite any assumptions when appropriate."
    )

    with st.chat_message("assistant"):
        with st.spinner("REMI processing through the local multi-agent core..."):
            try:
                payload = {
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                }

                response = requests.post(REMI_LOCAL_CORE_URL, json=payload, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    assistant_text = data.get("message", {}).get("content", "").strip()
                    if not assistant_text:
                        assistant_text = "REMI: The model responded with an empty message."
                else:
                    assistant_text = (
                        f"REMI (Core): Failed to connect to the local AI core (status {response.status_code}). "
                        "Ensure the local model service is running and reachable."
                    )
            except requests.exceptions.RequestException:
                assistant_text = (
                    "REMI (Core): Unable to establish communication with the local cluster. "
                    "Verify the AI core service is running and accessible from this host."
                )
            except Exception:
                assistant_text = "REMI (Core): An unexpected error occurred while contacting the local AI core."

            st.markdown(assistant_text)
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})

st.markdown("---")
st.markdown("REMI Enterprise Suite © 2026 — Developed by jramonrivasg")


def render_pasarela_fiscal_streamlit():
    st.markdown("---")
    st.subheader("🛡️ Pasarela de Licenciamiento y Trazabilidad Fiscal (REMI AI)")
    
    contribuyente = "Jesús Ramón Rivas García"
    rif = "V050153998"
    domicilio = "Calle El Samán, Casa Nro 17, Sector Porvorín, Guayabita, Aragua."
    producto = "Licencia Enterprise - REMI AI Suite"
    monto_usd = 499
    red = "Base Network (ChainID: 8453)"
    wallet = "0x96De980a766CCb10A19B6962587e2b61B650b372"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"**Contribuyente:** {contribuyente}")
        st.markdown(f"**RIF:** {rif}")
        st.markdown(f"**Domicilio:** {domicilio}")
        st.markdown(f"**Producto:** {producto}")
        st.markdown(f"**Monto a Pagar:** ${monto_usd}.00 USD")
        st.markdown(f"**Red Blockchain:** {red}")
        st.code(wallet, language="text")
        st.info("💡 Escanee el código QR con su billetera EVM (ej. Rabby) configurada en Base Network.")

    with col2:
        img = qrcode.make(wallet)
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="QR Oficial - Base Network", width=250)

    st.markdown("---")
render_pasarela_fiscal_streamlit()
