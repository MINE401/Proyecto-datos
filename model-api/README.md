README - model-api

Resumen
- API FastAPI para servir un modelo CatBoost.
- Contiene herramientas para generar encoders ordinales usados en producción (`scripts/save_encoders.py`).

Dependencias (instalar en el entorno):
```bash
pip install -r requirements.txt
```

Generar encoders ordinales
- Usa el script `scripts/save_encoders.py` para crear los encoders a partir del CSV de entrenamiento `df_company_tot.csv`.

Ejemplo:
```bash
python scripts/save_encoders.py --input /ruta/a/df_company_tot.csv --out artifacts
```

Esto generará en `artifacts/`:
- `encoder_revenue.joblib`
- `encoder_employee.joblib`
- `encoder_years.joblib`

Copiar luego estos archivos a la carpeta `artifacts/` del servidor donde se ejecuta la API.

Ejecutar la API (local):
```bash
uvicorn app:app --reload --port 8000
```

Notas
- Si no tienes `joblib` instalado, el script usará `pickle` como fallback, pero se recomienda `joblib`.
- Asegúrate de usar los mismos encoders que en entrenamiento para evitar desalineamiento en las codificaciones ordinales.
