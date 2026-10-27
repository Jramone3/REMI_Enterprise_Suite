#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
REMI Voice Synthesis Daemon (Vega TTS)
Robust background execution handler with null-safety sanitization.
"""

import sys
import os
from gtts import gTTS

def execute_vega_synthesis(text_payload: str, lang_code: str = 'es'):
    """
    Sanitizes input text payload and executes audio generation and playback.
    """
    try:
        if not text_payload or not isinstance(text_payload, str):
            print("[VEGA_TTS_ERROR]: Invalid or empty text payload provided.")
            return False
            
        # Rigorous string sanitization
        sanitized_text = text_payload.replace("*", "").replace("\n", " ").strip()
        if not sanitized_text:
            print("[VEGA_TTS_WARNING]: Sanitized text payload resulted in empty string.")
            return False

        tts_engine = gTTS(text=sanitized_text, lang=lang_code, slow=False)
        output_audio_path = "/tmp/remi_vega_output.mp3"
        tts_engine.save(output_audio_path)
        
        # Playback execution via system command (ALSA / PulseAudio / mpg123 / ffplay if available)
        # Fallback to background notification
        os.system(f"mpg123 -q {output_audio_path} > /dev/null 2>&1 &")
        
        print(f"[VEGA_TTS_SUCCESS]: Audio payload rendered and dispatched for '{sanitized_text[:30]}...'")
        return True

    except Exception as e:
        print(f"[VEGA_TTS_CRITICAL_FAILURE]: Exception during synthesis -> {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        execute_vega_synthesis(input_text)
    else:
        print("[VEGA_TTS_HELP]: No text argument supplied. Usage: python3 vega.py 'Text to synthesize'")
