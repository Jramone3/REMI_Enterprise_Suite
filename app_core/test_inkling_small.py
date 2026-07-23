from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_ID = "HuggingFaceTB/SmolLM-135M"

print("🔄 Cargando el motor en el búnker...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)

prompt = "Eres REMI, la ingeniera experta en ciberseguridad y sistemas del búnker de Ramón. Responde brevemente confirmando que los sistemas están listos:\n- Estado:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

print("🚀 Ejecutando prueba de inferencia optimizada...")
outputs = model.generate(
    **inputs, 
    max_new_tokens=60, 
    do_sample=True, 
    temperature=0.7, 
    repetition_penalty=1.2,
    eos_token_id=tokenizer.eos_token_id
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n--- RESPUESTA DEL NUEVO NÚCLEO DE REMI ---")
print(response)
