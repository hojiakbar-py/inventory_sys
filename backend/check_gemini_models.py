import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY topilmadi!")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("MAVJUD GEMINI MODELLARI:")
print("=" * 60)

# List all available models
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n[OK] Model: {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        print(f"   Supported methods: {model.supported_generation_methods}")
