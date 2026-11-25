import os

def generate_readme():
    content = """# REMI Enterprise Suite

Sovereign AI Core (Hybrid Cerebras + Ollama), Neural Graph & Multi-Pillar Orbital Perception Layer.

## Quick Start (FastAPI Gateway)
```bash
pip install -r requirements.txt
python main_api.py
```
It listens on port 5000 by default. Set the PORT environment variable to change it.
"""
    os.makedirs("docs", exist_ok=True)
    readme_path = "README.md"
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("README.md generado exitosamente.")
    except Exception as e:
        print(f"Error generando README: {e}")

if __name__ == "__main__":
    generate_readme()
