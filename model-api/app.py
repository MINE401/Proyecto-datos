# app.py (Ejemplo usando FastAPI)

from fastapi import FastAPI
from catboost import CatBoostClassifier, CatBoostRegressor
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from pydantic import BaseModel
from typing import Optional
from enum import Enum


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


# Inicializa la aplicación FastAPI
app = FastAPI(title="CatBoost Model API")

# --- 1. CARGA DEL MODELO (Solo se ejecuta una vez al inicio) ---
MODEL_PATH = "catboost_best_model.cbm"
model = None

@app.on_event("startup")
def load_model():
    """Carga el modelo CatBoost al iniciar la aplicación."""
    global model
    try:
        # Usa el método estático load_model y especifica el tipo si es necesario
        model = CatBoostClassifier() # O CatBoostRegressor()
        model.load_model(MODEL_PATH)
        print(f"✅ Modelo CatBoost cargado exitosamente desde: {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Error al cargar el modelo: {e}")
        # Es crucial que la app no inicie si no puede cargar el modelo

# --- 2. ENDPOINT DE PREDICCIÓN ---

# Define una estructura de datos para la entrada de la API (es una buena práctica)
class PredictionInput(BaseModel):
    company_id: Optional[int] = None
    revenue_band: Optional[RevenueBandEnum] = None
    employee_band: Optional[EmployeeBandEnum] = None
    years_in_business_band: Optional[YearsInBusinessEnum] = None
    global_region: Optional[str] = None
    industry_detail_customer: Optional[str] = None
    cloud_coverage: Optional[CloudCoverageEnum] = None
    technology_scope: Optional[TechnologyScopeEnum] = None
    partner_classification: Optional[PartnerClassificationEnum] = None


@app.post("/predict")
def predict(data: PredictionInput):
    """Realiza una predicción usando el modelo CatBoost cargado."""
    if model is None:
        return {"error": "El modelo no está cargado. La aplicación no se inició correctamente."}

    try:
        # Mapear los campos Pydantic a los nombres que usa feature_engineering
        # Si algunos campos vienen como Enum, extraer su .value; si no, dejar None/str
        payload = {
            'Company ID': data.company_id,
            'Revenue Band': data.revenue_band.value if data.revenue_band is not None else None,
            'Employee Band': data.employee_band.value if data.employee_band is not None else None,
            'Years in Business Band': data.years_in_business_band.value if data.years_in_business_band is not None else None,
            'Global Region': data.global_region,
            'Industry Detail (Customer)': data.industry_detail_customer,
            'Cloud Coverage': data.cloud_coverage.value if data.cloud_coverage is not None else None,
            'Technology Scope': data.technology_scope.value if data.technology_scope is not None else None,
            'Partner Classification': data.partner_classification.value if data.partner_classification is not None else None
        }

        # Preparar DataFrame de entrada y aplicar feature engineering
        features_df = pd.DataFrame([payload])
        features_transformed = feature_engineering(features_df)

        # Quitar columnas que no son usadas por el modelo
        X = features_transformed.drop(['Relevance', 'Company ID'], axis=1, errors='ignore')

        # Predecir
        prediction = model.predict(X)
        prediction_proba = None
        if hasattr(model, 'predict_proba'):
            try:
                prediction_proba = model.predict_proba(X).tolist()
            except Exception:
                prediction_proba = None

        result = {
            "prediction": prediction.tolist(),
            "model_used": "CatBoost"
        }
        if prediction_proba is not None:
            result['prediction_proba'] = prediction_proba

        return result
    except Exception as e:
        return {"error": f"Error durante la predicción: {e}"}

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}


def feature_engineering(input_data):
    """
    Aplica transformaciones de ingeniería de características a los datos de entrada.
    Replica el procesamiento del notebook 1_Preparación_score.ipynb
    """
    output_data = input_data.copy()
    
    # ========================================
    # 1. TRANSFORMACIÓN: Revenue Band
    # ========================================
    if 'Revenue Band' in output_data:
        output_data['Revenue Band Mod'] = (
            output_data['Revenue Band']
            .astype(str)
            .str.replace('K', '000', regex=False)
            .str.replace('.5M', '500000', regex=False)
            .str.replace('M', '000000', regex=False)
            .str.replace('B', '000000000', regex=False)
            .str.replace('$', '', regex=False)
            .str.replace('+', '', regex=False)
            .str.split('-')
            .str[0]
            .str.replace('<', '-', regex=False)
            .astype(float)
        )
        
        # Codificación ordinal
        encoder_revenue = OrdinalEncoder()
        output_data['Revenue Band Mod Codificado'] = encoder_revenue.fit_transform(
            output_data[['Revenue Band Mod']]
        )
    
    # ========================================
    # 2. TRANSFORMACIÓN: Employee Band
    # ========================================
    if 'Employee Band' in output_data:
        output_data['Employee Band Mod'] = (
            output_data['Employee Band']
            .astype(str)
            .str.replace('+', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.split('-')
            .str[0]
            .astype(float)
        )
        
        # Codificación ordinal
        encoder_employee = OrdinalEncoder()
        output_data['Employee Band Mod Codificado'] = encoder_employee.fit_transform(
            output_data[['Employee Band Mod']]
        )
    
    # ========================================
    # 3. TRANSFORMACIÓN: Years in Business Band
    # ========================================
    if 'Years in Business Band' in output_data:
        output_data['Years in Business Band Mod'] = (
            output_data['Years in Business Band']
            .astype(str)
            .str.replace('+', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace('<', '', regex=False)
            .str.split('-')
            .str[0]
        )
        output_data['Years in Business Band Mod'] = (
            output_data['Years in Business Band Mod']
            .replace('', np.nan)
            .astype(float)
        )
        
        # Codificación ordinal
        encoder_years = OrdinalEncoder()
        output_data['Years in Business Band Mod Codificado'] = encoder_years.fit_transform(
            output_data[['Years in Business Band Mod']]
        )
    
    # ========================================
    # 4. TRANSFORMACIÓN: Global Region (moda por empresa)
    # ========================================
    if 'Global Region' in output_data:
        # Si es un único registro, mantenerlo; si es múltiple, usar moda
        if isinstance(output_data['Global Region'], str):
            output_data['Global Region'] = output_data['Global Region']
        # Para múltiples registros se aplicaría moda en producción
    
    # ========================================
    # 5. TRANSFORMACIÓN: Industry Detail (Customer)
    # ========================================
    if 'Industry Detail (Customer)' in output_data:
        def map_industry(code):
            if pd.isna(code):
                return np.nan
            code = str(code).strip().upper()
            
            if code.startswith("B"):
                return "Finanzas"
            elif code.startswith("C"):
                return "Salud"
            elif code.startswith("D"):
                return "Energia"
            elif code.startswith("E"):
                return "Manufactura"
            elif code.startswith("F"):
                return "Servicios"
            elif code.startswith("G"):
                return "Sector_publico"
            elif code.startswith("H"):
                return "Otros"
            else:
                return "Otros"
        
        output_data['Industry_agrupado'] = output_data['Industry Detail (Customer)'].apply(map_industry)
    
    # ========================================
    # 6. TRANSFORMACIÓN: Cloud Coverage
    # ========================================
    if 'Cloud Coverage' in output_data:
        output_data['Cloud_agrupado'] = output_data['Cloud Coverage'].apply(
            lambda x: 'Publico' if x in ['Iaas', 'SaaS', 'PaaS'] else 'Otros'
        )
    
    # ========================================
    # 7. TRANSFORMACIÓN: Technology Scope
    # ========================================
    if 'Technology Scope' in output_data:
        infraestructura = ['Mobility', 'IoT', 'Cloud']
        inteligencia = ['Big Data and Analytics', 'AI', 'Robotics']
        usuario = ['AR/VR', '3D Printing', 'Social']
        seguridad = ['Security', 'Blockchain']
        
        def map_tech(scope):
            if pd.isna(scope):
                return np.nan
            s = str(scope).strip()
            
            if s in infraestructura:
                return 'Infraestructura'
            elif s in inteligencia:
                return 'Inteligencia'
            elif s in usuario:
                return 'Usuario'
            elif s in seguridad:
                return 'Seguridad'
            elif s == '-':
                return 'Otros'
            else:
                return 'Otros'
        
        output_data['Technology_agrupado'] = output_data['Technology Scope'].apply(map_tech)
    
    # ========================================
    # 8. TRANSFORMACIÓN: Partner Classification
    # ========================================
    if 'Partner Classification' in output_data:
        desarrollador = ['Independent Software Vendor (ISV)']
        integrador = ['Regional System Integrator (RSI)', 'Global Systems Integrator (GSI)']
        proveedor = ['Cloud Service Provider (CSP)', 'Managed Service Provider (MSP)']
        revendedor = ['Direct Market Reseller (DMR)', 'Value Added Reseller (VAR)', 'Distributor']
        
        def map_partner(p):
            if pd.isna(p):
                return np.nan
            s = str(p).strip()
            
            if s in desarrollador:
                return "Desarrollador"
            elif s in integrador:
                return "Integrador"
            elif s in proveedor:
                return "Proveedor"
            elif s in revendedor:
                return "Revendedor"
            elif s == '-':
                return "Otros"
            else:
                return "Otros"
        
        output_data['Partner_agrupado'] = output_data['Partner Classification'].apply(map_partner)
    
    # ========================================
    # 9. IMPUTACIÓN DE NULOS
    # ========================================
    # Ordinales: rellenar con mediana
    ordinales = [
        'Revenue Band Mod Codificado',
        'Employee Band Mod Codificado',
        'Years in Business Band Mod Codificado'
    ]
    
    for col in ordinales:
        if col in output_data.columns:
            mediana = output_data[col].median()
            output_data[col] = output_data[col].fillna(mediana)
    
    # Categóricas: rellenar con 'Otros'
    categoricas = [
        'Global Region',
        'Industry_agrupado',
        'Cloud_agrupado',
        'Technology_agrupado',
        'Partner_agrupado'
    ]
    
    for col in categoricas:
        if col in output_data.columns:
            output_data[col] = output_data[col].fillna('Otros')
    
    return output_data