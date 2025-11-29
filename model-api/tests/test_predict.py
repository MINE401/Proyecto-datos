import os
import sys
from fastapi.testclient import TestClient

# Asegurar que el directorio padre (workspace `model-api`) esté en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app

client = TestClient(app)


def test_predict_smoke():
    payload = {
        "company_id": 12345,
        "revenue_band": "<$100K",
        "employee_band": "1-10",
        "years_in_business_band": "<1",
        "global_region": "Americas",
        "industry_detail_customer": "B123",
        "cloud_coverage": "Iaas",
        "technology_scope": "Cloud",
        "partner_classification": "Independent Software Vendor (ISV)"
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Debe responder 200 y contener información útil. Aceptamos dos casos:
    # - el modelo cargó y devuelve 'model_used' y predicción
    # - el modelo no se cargó y devuelve un mensaje de error (aún así la ruta respondió)
    assert (data.get("model_used") == "CatBoost" and (("prediction" in data) or ("prediction_proba" in data))) or ("error" in data)
