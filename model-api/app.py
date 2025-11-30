# app.py (Ejemplo usando FastAPI)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from catboost import CatBoostClassifier, CatBoostRegressor
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from pydantic import BaseModel
from typing import Optional
from enum import Enum
import os
try:
    from joblib import dump, load
except Exception:
    import pickle
    def dump(obj, path):
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)


# --- Enums para campos categóricos (valores esperados según notebook / dataframes) ---
class RevenueBandEnum(str, Enum):
    less_100K = "<$100K"
    _100k_499k = "$100K-$499K"
    _500k_999k = "$500K-$999K"
    _1m_2_49m = "$1M-$2.49M"
    _2_5m_4_9m = "$2.5M-$4.9M"
    _5m_9_9m = "$5M-$9.9M"
    _10m_24_9m = "$10M-$24.9M"
    _25m_49m = "$25M-$49M"
    _50m_99m = "$50M-$99M"
    _100m_499m = "$100M-$499M"
    _500m_999m = "$500M-$999M"
    _1b_4_9b = "$1B-$4.9B"
    _5b_9_9b = "$5B-$9.9B"
    _10b_24_9b = "$10B-$24.9B"
    _25b_plus = "$25B+"


class CloudCoverageEnum(str, Enum):
    Iaas = "Iaas"
    SaaS = "SaaS"
    PaaS = "PaaS"
    Other = "Other"


class TechnologyScopeEnum(str, Enum):
    Mobility = "Mobility"
    IoT = "IoT"
    Cloud = "Cloud"
    BigDataAndAnalytics = "Big Data and Analytics"
    AI = "AI"
    Robotics = "Robotics"
    AR_VR = "AR/VR"
    ThreeD_Printing = "3D Printing"
    Social = "Social"
    Security = "Security"
    Blockchain = "Blockchain"
    Other = "-"


class PartnerClassificationEnum(str, Enum):
    ISV = "Independent Software Vendor (ISV)"
    RSI = "Regional System Integrator (RSI)"
    GSI = "Global Systems Integrator (GSI)"
    CSP = "Cloud Service Provider (CSP)"
    MSP = "Managed Service Provider (MSP)"
    DMR = "Direct Market Reseller (DMR)"
    VAR = "Value Added Reseller (VAR)"
    Distributor = "Distributor"
    Other = "-"


class IndustryAgrpEnum(str, Enum):
    Finanzas = "Finanzas"
    Salud = "Salud"
    Energia = "Energia"
    Manufactura = "Manufactura"
    Servicios = "Servicios"
    Sector_publico = "Sector_publico"
    Otros = "Otros"


# Enums adicionales solicitados: Employee Band y Years in Business Band
class EmployeeBandEnum(str, Enum):
    _1_10 = "1-10"
    _11_50 = "11-50"
    _51_200 = "51-200"
    _201_500 = "201-500"
    _501_1000 = "501-1000"
    _1001_5000 = "1001-5000"
    _5001_plus = "5001+"


class YearsInBusinessEnum(str, Enum):
    less_1 = "<1"
    _1_2 = "1-2"
    _3_5 = "3-5"
    _6_10 = "6-10"
    _11_20 = "11-20"
    _21_plus = "21+"


# Configurar logging básico
logger = logging.getLogger("model_api")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# --- 1. CARGA DEL MODELO (Solo se ejecuta una vez al inicio) ---
MODEL_PATH = "catboost_best_model.cbm"
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja los eventos de startup y shutdown de la aplicación usando lifespan."""
    # Startup
    global model
    try:
        # Usa el método estático load_model y especifica el tipo si es necesario
        model = CatBoostClassifier() # O CatBoostRegressor()
        model.load_model(MODEL_PATH)
        logger.info(f"Modelo CatBoost cargado exitosamente desde: {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error al cargar el modelo: {e}")
        # Es crucial que la app no inicie si no puede cargar el modelo
    # Yield control a la aplicación durante su ejecución
    yield
    # Shutdown (lógica de limpieza si es necesaria)
    logger.info("Aplicación cerrando")

# Inicializa la aplicación FastAPI con lifespan handler
app = FastAPI(title="CatBoost Model API", lifespan=lifespan)

# --- 2. ENDPOINT DE PREDICCIÓN ---

# Define una estructura de datos para la entrada de la API (es una buena práctica)
class PredictionInput(BaseModel):
    company_id: Optional[int] = None
    # Acepta cualquier string y se mapea internamente para evitar 422 por valores fuera del Enum
    revenue_band: Optional[str] = None
    employee_band: Optional[str] = None
    years_in_business_band: Optional[str] = None
    global_region: Optional[str] = None
    industry_detail_customer: Optional[str] = None
    cloud_coverage: Optional[str] = None
    technology_scope: Optional[str] = None
    partner_classification: Optional[str] = None

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
def predict(data: PredictionInput):
    """Realiza una predicción usando el modelo CatBoost cargado."""
    if model is None:
        return {"error": "El modelo no está cargado. La aplicación no se inició correctamente."}

    try:
        # Si algunos campos vienen como Enum, extraer su .value; si no, dejar None/str
        # Normalizar valores de entrada para tolerar variaciones de mayúsculas/minúsculas y espacios
        def norm(v):
            if v is None:
                return None
            if isinstance(v, str):
                return v.strip()
            return v

        # Mapeos tolerantes para variantes comunes desde el front
        def map_cloud(v):
            s = norm(v)
            if s is None:
                return None
            s_upper = s.upper()
            if s_upper == 'IAAS':
                return 'Iaas'
            if s_upper == 'PAAS':
                return 'PaaS'
            if s_upper == 'SAAS':
                return 'SaaS'
            return s

        def map_technology(v):
            s = norm(v)
            if s is None:
                return None
            # Normalizar variantes comunes
            aliases = {
                'mobility': 'Mobility',
                'iot': 'IoT',
                'cloud': 'Cloud',
                'big data and analytics': 'Big Data and Analytics',
                'bigdataandanalytics': 'Big Data and Analytics',
                'ai': 'AI',
                'robotics': 'Robotics',
                'ar/vr': 'AR/VR',
                'arvr': 'AR/VR',
                '3d printing': '3D Printing',
                '3dprinting': '3D Printing',
                'social': 'Social',
                'security': 'Security',
                'blockchain': 'Blockchain',
                '-': '-',
            }
            key = s.lower().replace(' ', '') if s.lower() not in aliases else s.lower()
            return aliases.get(s.lower(), aliases.get(key, s))

        def map_partner(v):
            s = norm(v)
            if s is None:
                return None
            aliases = {
                'independent software vendor (isv)': 'Independent Software Vendor (ISV)',
                'isv': 'Independent Software Vendor (ISV)',
                'regional system integrator (rsi)': 'Regional System Integrator (RSI)',
                'rsi': 'Regional System Integrator (RSI)',
                'global systems integrator (gsi)': 'Global Systems Integrator (GSI)',
                'gsi': 'Global Systems Integrator (GSI)',
                'cloud service provider (csp)': 'Cloud Service Provider (CSP)',
                'csp': 'Cloud Service Provider (CSP)',
                'managed service provider (msp)': 'Managed Service Provider (MSP)',
                'msp': 'Managed Service Provider (MSP)',
                'direct market reseller (dmr)': 'Direct Market Reseller (DMR)',
                'dmr': 'Direct Market Reseller (DMR)',
                'value added reseller (var)': 'Value Added Reseller (VAR)',
                'var': 'Value Added Reseller (VAR)',
                'distributor': 'Distributor',
                '-': '-',
            }
            key = s.lower()
            return aliases.get(key, s)

        payload = {
            'Company ID': data.company_id,
            'Revenue Band': norm(data.revenue_band),
            'Employee Band': norm(data.employee_band),
            'Years in Business Band': norm(data.years_in_business_band),
            'Global Region': norm(data.global_region),
            'Industry Detail (Customer)': norm(data.industry_detail_customer),
            'Cloud Coverage': map_cloud(data.cloud_coverage),
            'Technology Scope': map_technology(data.technology_scope),
            'Partner Classification': map_partner(data.partner_classification)
        }

        # Preparar DataFrame de entrada y aplicar feature engineering
        features_df = pd.DataFrame([payload])
        features_transformed = feature_engineering(features_df)

        # (debug prints removed)

        # Quitar columnas que no son usadas por el modelo
        X = features_transformed.drop(['Relevance', 'Company ID'], axis=1, errors='ignore')

        # Alinear columnas con las que el modelo espera (evita errores por nombres distintos)
        def _get_model_feature_names(m):
            # Intentar varios atributos/métodos que puede tener un modelo CatBoost
            for attr in ('feature_names_', 'feature_names', 'get_feature_names'):
                if hasattr(m, attr):
                    val = getattr(m, attr)
                    if callable(val):
                        try:
                            return list(val())
                        except Exception:
                            continue
                    else:
                        return list(val)
            return None

        expected = _get_model_feature_names(model)
        # (debug prints removed)
        if expected is not None and len(expected) > 0:
            # Añadir columnas faltantes con NaN (el modelo deberá manejarlas o se pueden imputar)
            for col in expected:
                if col not in X.columns:
                    X[col] = np.nan
            # Seleccionar/ordenar solo las columnas esperadas (descartar extras)
            X = X[expected]
        else:
            # Fallback: si el modelo no expone nombres y existe una columna 'Revenue Band Mod'
            # pero falta 'Revenue Band', renombrarla para evitar el error observado.
            if 'Revenue Band Mod' in X.columns and 'Revenue Band' not in X.columns:
                X = X.rename(columns={'Revenue Band Mod': 'Revenue Band'})

        # (debug prints removed)

        # Predecir: intentar predict normal, si falla por mapeo de etiquetas usar alternativas
        prediction = None
        prediction_proba = None
        try:
            prediction = model.predict(X)
        except Exception as e_pred:
            # Intentar obtener probabilidades (si aplica)
            try:
                prediction_proba = model.predict(X, prediction_type='Probability')
                prediction = None
            except Exception:
                try:
                    # Último recurso: obtener valores crudos
                    prediction = model.predict(X, prediction_type='RawFormulaVal')
                except Exception as e2:
                    raise e2
        # Si no obtuvimos probabilidades pero el modelo tiene predict_proba, intentarlo
        if prediction_proba is None and hasattr(model, 'predict_proba'):
            try:
                prediction_proba = model.predict_proba(X).tolist()
            except Exception:
                prediction_proba = None

        result = {"model_used": "CatBoost"}
        if prediction is not None:
            try:
                result['prediction'] = prediction.tolist()
            except Exception:
                result['prediction'] = prediction
        if prediction_proba is not None:
            try:
                result['prediction_proba'] = prediction_proba.tolist() if hasattr(prediction_proba, 'tolist') else prediction_proba
            except Exception:
                result['prediction_proba'] = prediction_proba

        return result
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # Registrar la traza en logs del servidor (no se devuelve en la respuesta)
        try:
            logger.exception("Error durante /predict:\n%s", tb)
        except Exception:
            pass
        return {"error": f"Error durante la predicción: {e}"}

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}


def feature_engineering(input_data):
    """
    Aplica transformaciones de ingeniería de características a los datos de entrada.
    Replica (de forma simplificada) el procesamiento del notebook 1_Preparación_score.ipynb
    - Normaliza bands (Revenue / Employee / Years)
    - Agrupa categorías (Industry, Cloud, Technology, Partner)
    - Reusa encoders ordinales guardados en `artifacts/` si existen
    """
    output_data = input_data.copy()

    # Helper: safe string
    def sstr(x):
        return None if x is None or (isinstance(x, float) and np.isnan(x)) else str(x)

    # Directorio de artefactos
    enc_dir = 'artifacts'
    os.makedirs(enc_dir, exist_ok=True)

    # ===== Revenue Band =====
    if 'Revenue Band' in output_data.columns:
        # Normalizar texto y extraer límite inferior
        output_data['Revenue Band Mod'] = (
            output_data['Revenue Band'].fillna('').astype(str)
            .str.replace('K', '000', regex=False)
            .str.replace('.5M', '500000', regex=False)
            .str.replace('M', '000000', regex=False)
            .str.replace('B', '000000000', regex=False)
            .str.replace('$', '', regex=False)
            .str.replace('+', '', regex=False)
            .str.split('-').str[0]
            .str.replace('<', '-', regex=False)
        )
        # Convertir a float cuando sea posible
        output_data['Revenue Band Mod'] = pd.to_numeric(output_data['Revenue Band Mod'], errors='coerce')

        rev_path = os.path.join(enc_dir, 'encoder_revenue.joblib')
        try:
            if os.path.exists(rev_path):
                encoder_revenue = load(rev_path)
            else:
                encoder_revenue = OrdinalEncoder()
                encoder_revenue.fit(output_data[['Revenue Band Mod']].fillna(-1).to_numpy())
                dump(encoder_revenue, rev_path)
        except Exception:
            encoder_revenue = OrdinalEncoder()
            encoder_revenue.fit(output_data[['Revenue Band Mod']].fillna(-1))

        # Usar .to_numpy() para evitar verificación por nombre de columna en encoders guardados
        arr_rev = output_data[['Revenue Band Mod']].fillna(-1).to_numpy(dtype=float)
        try:
            allowed_rev = set([float(x) for x in encoder_revenue.categories_[0]])
            arr_rev = np.where(np.isin(arr_rev, list(allowed_rev)), arr_rev, -1.0)
        except Exception:
            pass
        transformed_rev = encoder_revenue.transform(arr_rev)
        output_data['Revenue Band Mod Codificado'] = transformed_rev.reshape(-1, 1) if transformed_rev.ndim == 2 else transformed_rev

    # ===== Employee Band =====
    if 'Employee Band' in output_data.columns:
        output_data['Employee Band Mod'] = (
            output_data['Employee Band'].fillna('').astype(str)
            .str.replace('+', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.split('-').str[0]
        )
        output_data['Employee Band Mod'] = pd.to_numeric(output_data['Employee Band Mod'], errors='coerce')

        emp_path = os.path.join(enc_dir, 'encoder_employee.joblib')
        try:
            if os.path.exists(emp_path):
                encoder_employee = load(emp_path)
            else:
                encoder_employee = OrdinalEncoder()
                encoder_employee.fit(output_data[['Employee Band Mod']].fillna(-1).to_numpy())
                dump(encoder_employee, emp_path)
        except Exception:
            encoder_employee = OrdinalEncoder()
            encoder_employee.fit(output_data[['Employee Band Mod']].fillna(-1))

        arr_emp = output_data[['Employee Band Mod']].fillna(-1).to_numpy(dtype=float)
        try:
            allowed_emp = set([float(x) for x in encoder_employee.categories_[0]])
            arr_emp = np.where(np.isin(arr_emp, list(allowed_emp)), arr_emp, -1.0)
        except Exception:
            pass
        transformed_emp = encoder_employee.transform(arr_emp)
        output_data['Employee Band Mod Codificado'] = transformed_emp.reshape(-1, 1) if transformed_emp.ndim == 2 else transformed_emp

    # ===== Years in Business Band =====
    if 'Years in Business Band' in output_data.columns:
        output_data['Years in Business Band Mod'] = (
            output_data['Years in Business Band'].fillna('').astype(str)
            .str.replace('+', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace('<', '', regex=False)
            .str.split('-').str[0]
        )
        output_data['Years in Business Band Mod'] = pd.to_numeric(output_data['Years in Business Band Mod'], errors='coerce')

        years_path = os.path.join(enc_dir, 'encoder_years.joblib')
        try:
            if os.path.exists(years_path):
                encoder_years = load(years_path)
            else:
                encoder_years = OrdinalEncoder()
                encoder_years.fit(output_data[['Years in Business Band Mod']].fillna(-1).to_numpy())
                dump(encoder_years, years_path)
        except Exception:
            encoder_years = OrdinalEncoder()
            encoder_years.fit(output_data[['Years in Business Band Mod']].fillna(-1))

        arr_years = output_data[['Years in Business Band Mod']].fillna(-1).to_numpy(dtype=float)
        try:
            allowed_years = set([float(x) for x in encoder_years.categories_[0]])
            arr_years = np.where(np.isin(arr_years, list(allowed_years)), arr_years, -1.0)
        except Exception:
            pass
        transformed_years = encoder_years.transform(arr_years)
        output_data['Years in Business Band Mod Codificado'] = transformed_years.reshape(-1, 1) if transformed_years.ndim == 2 else transformed_years

    # ===== Industry grouping =====
    if 'Industry Detail (Customer)' in output_data.columns:
        def map_industry(code):
            if pd.isna(code) or code == 'None':
                return np.nan
            code = str(code).strip().upper()
            if code.startswith('B'):
                return 'Finanzas'
            if code.startswith('C'):
                return 'Salud'
            if code.startswith('D'):
                return 'Energia'
            if code.startswith('E'):
                return 'Manufactura'
            if code.startswith('F'):
                return 'Servicios'
            if code.startswith('G'):
                return 'Sector_publico'
            return 'Otros'
        output_data['Industry_agrupado'] = output_data['Industry Detail (Customer)'].apply(map_industry)

    # ===== Cloud Coverage grouping =====
    if 'Cloud Coverage' in output_data.columns:
        output_data['Cloud_agrupado'] = output_data['Cloud Coverage'].apply(lambda x: 'Publico' if sstr(x) in ['Iaas', 'SaaS', 'PaaS'] else 'Otros')

    # ===== Technology grouping =====
    if 'Technology Scope' in output_data.columns:
        infraestructura = ['Mobility', 'IoT', 'Cloud']
        inteligencia = ['Big Data and Analytics', 'AI', 'Robotics']
        usuario = ['AR/VR', '3D Printing', 'Social']
        seguridad = ['Security', 'Blockchain']
        def map_tech(scope):
            if pd.isna(scope) or scope == 'None':
                return np.nan
            s = str(scope).strip()
            if s in infraestructura:
                return 'Infraestructura'
            if s in inteligencia:
                return 'Inteligencia'
            if s in usuario:
                return 'Usuario'
            if s in seguridad:
                return 'Seguridad'
            return 'Otros'
        output_data['Technology_agrupado'] = output_data['Technology Scope'].apply(map_tech)

    # ===== Partner grouping =====
    if 'Partner Classification' in output_data.columns:
        desarrollador = ['Independent Software Vendor (ISV)']
        integrador = ['Regional System Integrator (RSI)', 'Global Systems Integrator (GSI)']
        proveedor = ['Cloud Service Provider (CSP)', 'Managed Service Provider (MSP)']
        revendedor = ['Direct Market Reseller (DMR)', 'Value Added Reseller (VAR)', 'Distributor']
        def map_partner(p):
            if pd.isna(p) or p == 'None':
                return np.nan
            s = str(p).strip()
            if s in desarrollador:
                return 'Desarrollador'
            if s in integrador:
                return 'Integrador'
            if s in proveedor:
                return 'Proveedor'
            if s in revendedor:
                return 'Revendedor'
            return 'Otros'
        output_data['Partner_agrupado'] = output_data['Partner Classification'].apply(map_partner)

    # ===== Imputaciones =====
    ordinales = ['Revenue Band Mod Codificado', 'Employee Band Mod Codificado', 'Years in Business Band Mod Codificado']
    for col in ordinales:
        if col in output_data.columns:
            med = output_data[col].median()
            output_data[col] = output_data[col].fillna(med)

    categoricas = ['Global Region', 'Industry_agrupado', 'Cloud_agrupado', 'Technology_agrupado', 'Partner_agrupado']
    for col in categoricas:
        if col in output_data.columns:
            output_data[col] = output_data[col].fillna('Otros')

    return output_data