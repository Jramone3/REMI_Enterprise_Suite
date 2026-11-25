#!/usr/bin/env python3
"""
REMI_CORE - Graph Engine & Intent Router
Máquina de estados determinista para comandos, subcomandos y argumentos.
"""

import json
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "commands_map.json")

def load_commands():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"prefix": "/", "commands": {}, "subcommands": {}}

def route_intent(user_input):
    config = load_commands()
    prefix = config.get("prefix", "/")
    
    if user_input.startswith(prefix):
        parts = user_input[len(prefix):].strip().split(" ", 2)
        cmd = parts[0].lower()
        subcmd = parts[1] if len(parts) > 1 else ""
        args = parts[2] if len(parts) > 2 else ""
        
        commands_list = config.get("commands", {})
        if cmd in commands_list:
            return {
                "status": "DIRECT_ROUTE",
                "command": cmd,
                "subcommand": subcmd,
                "args": args,
                "description": commands_list[cmd]
            }
            
    return {"status": "LLM_FALLBACK", "prompt": user_input}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_input = sys.argv[1]
        result = route_intent(test_input)
        print(json.dumps(result, indent=2))
    else:
        print("Uso: python3 graph_engine.py '/comando subcomando arg'")
