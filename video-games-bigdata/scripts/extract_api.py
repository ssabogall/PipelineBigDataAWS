import requests
import json
import os

from dotenv import load_dotenv

# ==========================================
# CONFIG
# ==========================================
load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")

URL = f"https://api.rawg.io/api/games?key={API_KEY}"

# ==========================================
# REQUEST
# ==========================================

response = requests.get(URL)

data = response.json()

# ==========================================
# CREAR CARPETAS
# ==========================================

os.makedirs("../data/raw", exist_ok=True)

# ==========================================
# GUARDAR JSON
# ==========================================

with open("../data/raw/games_raw.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("JSON guardado correctamente")