#!/usr/bin/env python3
"""
REMI Enterprise Suite - Streamlit Interactive Demo (standardized English)
This demo showcases:
- Enterprise license issuance (demo-only; replace with secure backend in production)
- License verification and update synchronization checks
- Local multi-agent core chat client (connect to a local LLM REST endpoint)

Notes for production:
- Do not rely on client-side license generation. Use a secure signing server/HSM.
- Validate on-chain transfers through a back-end provider and keep an auditable record.
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

    # Payment data toggle
    if st.button("Generate Payment Data"):
        st.session_state.show_payment = True

    if st.session_state.get("show_payment", False):
        st.info(
            "**Direct Payment Instructions:**\n\n"
            "1. Send **499 USDT (ERC-20 / Base)** or equivalent in ETH/BNB to:\n"
            "`0x96De980a766CCb10A19B6962587e2b61B650b372`\n\n"
            "2. Register your purchaser email and provide the transaction hash (TxHash) to receive your annual license key."
        )

        # Registration form for license activation (demo)
        purchaser_email = st.text_input("Registration email:")
        tx_hash = st.text_input("Transaction hash (TxHash):")

        if st.button("Verify and Activate Annual License"):
            if purchaser_email and tx_hash:
                # Demo license generation logic:
                # In production, perform on-chain verification and sign license server-side
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
            # Demo verification response: in production, query license database and update server
            st.success(
                "License active. Cluster synchronized to the latest security patch available for this release."
            )
        else:
            st.warning("Please enter your registered credentials (email and license key).")

# Main interface: Local multi-agent core chat
st.info("Welcome to the REMI interactive showcase. Enter a query to interact with the local AI core.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input (user)
if prompt := st.chat_input("Type a query or instruction for REMI:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build system prompt for the local model
    system_prompt = (
        "You are REMI, the AI core of REMI Enterprise Suite — an enterprise multi-agent framework. "
        "Respond in a technical, professional, analytical, and executive tone. Provide clear, actionable guidance "
        "and cite any assumptions when appropriate."
    )

    # Call local LLM-compatible REST API (demo)
    with st.chat_message("assistant"):
        with st.spinner("REMI processing through the local multi-agent core..."):
            try:
                api_url = os.environ.get("REMI_LOCAL_CORE_URL", "http://localhost:11434/api/chat")
                payload = {
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                }

                response = requests.post(api_url, json=payload, timeout=20)
                if response.status_code == 200:
                    # Expected shape: { "message": { "content": "..." } }
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
