from sodapy import Socrata
import json
import os

# Recomendado: usar variable de entorno
APP_TOKEN = os.getenv("SOC_DATA_TOKEN") or "eKmXxs87I1RYHCKAnF5fAiLVK"

client = Socrata("www.datos.gov.co", APP_TOKEN)

# Traer todos los campos y la geometría
results = client.get(
    "68qj-5xux",
    select="*",
    limit=2000
)

# Mostrar como JSON
print(json.dumps(results, indent=2, ensure_ascii=False))
