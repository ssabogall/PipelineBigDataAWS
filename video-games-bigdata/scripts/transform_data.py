import pandas as pd
import json

# ==========================================
# LEER JSON
# ==========================================

with open("../data/raw/games_raw.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# ==========================================
# EXTRAER JUEGOS
# ==========================================

games = data["results"]

# ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(games)

# ==========================================
# COLUMNAS IMPORTANTES
# ==========================================

df_clean = df[
    [
        "id",
        "name",
        "released",
        "rating",
        "metacritic"
    ]
]

# ==========================================
# GUARDAR CSV
# ==========================================

df_clean.to_csv(
    "../data/processed/games.csv",
    index=False
)

print("CSV generado correctamente")