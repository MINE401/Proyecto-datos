"""scripts/save_encoders.py

Genera y guarda los OrdinalEncoders usados en producción.

Uso:
    python scripts/save_encoders.py --input /ruta/al/df_company_tot.csv --out artifacts/

El script aplica las mismas transformaciones que el notebook:
 - Revenue Band -> Revenue Band Mod (numérico) -> encoder_revenue.joblib
 - Employee Band -> Employee Band Mod (numérico) -> encoder_employee.joblib
 - Years in Business Band -> Years in Business Band Mod (numérico) -> encoder_years.joblib

El script usa joblib si está disponible, si no usa pickle como fallback.
"""

import os
import argparse
import sys
import pandas as pd
import numpy as np

try:
    from joblib import dump
except Exception:
    import pickle
    def dump(obj, path):
        with open(path, 'wb') as f:
            pickle.dump(obj, f)

from sklearn.preprocessing import OrdinalEncoder


def normalize_revenue(series: pd.Series) -> pd.Series:
    s = series.fillna('').astype(str)
    s = (s
         .str.replace('K', '000', regex=False)
         .str.replace('.5M', '500000', regex=False)
         .str.replace('M', '000000', regex=False)
         .str.replace('B', '000000000', regex=False)
         .str.replace('$', '', regex=False)
         .str.replace('+', '', regex=False)
         .str.split('-').str[0]
         .str.replace('<', '-', regex=False)
        )
    return pd.to_numeric(s, errors='coerce')


def normalize_employee(series: pd.Series) -> pd.Series:
    s = series.fillna('').astype(str)
    s = (s
         .str.replace('+', '', regex=False)
         .str.replace(',', '', regex=False)
         .str.split('-').str[0]
        )
    return pd.to_numeric(s, errors='coerce')


def normalize_years(series: pd.Series) -> pd.Series:
    s = series.fillna('').astype(str)
    s = (s
         .str.replace('+', '', regex=False)
         .str.replace(' ', '', regex=False)
         .str.replace('<', '', regex=False)
         .str.split('-').str[0]
        )
    return pd.to_numeric(s, errors='coerce')


def main(input_csv: str, out_dir: str):
    if not os.path.exists(input_csv):
        print(f"Error: no se encontró el archivo {input_csv}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)

    df = pd.read_csv(input_csv)
    print(f"Cargado {input_csv} -> {df.shape[0]} filas, {df.shape[1]} columnas")

    # Revenue
    if 'Revenue Band' in df.columns:
        rev_mod = normalize_revenue(df['Revenue Band'])
        rev_vals = rev_mod.fillna(-1).to_frame()
        encoder_revenue = OrdinalEncoder()
        encoder_revenue.fit(rev_vals)
        path = os.path.join(out_dir, 'encoder_revenue.joblib')
        dump(encoder_revenue, path)
        print(f"Guardado encoder_revenue en: {path}")
    else:
        print("Warning: columna 'Revenue Band' no encontrada en el CSV")

    # Employee
    if 'Employee Band' in df.columns:
        emp_mod = normalize_employee(df['Employee Band'])
        emp_vals = emp_mod.fillna(-1).to_frame()
        encoder_employee = OrdinalEncoder()
        encoder_employee.fit(emp_vals)
        path = os.path.join(out_dir, 'encoder_employee.joblib')
        dump(encoder_employee, path)
        print(f"Guardado encoder_employee en: {path}")
    else:
        print("Warning: columna 'Employee Band' no encontrada en el CSV")

    # Years in Business
    if 'Years in Business Band' in df.columns:
        years_mod = normalize_years(df['Years in Business Band'])
        years_vals = years_mod.fillna(-1).to_frame()
        encoder_years = OrdinalEncoder()
        encoder_years.fit(years_vals)
        path = os.path.join(out_dir, 'encoder_years.joblib')
        dump(encoder_years, path)
        print(f"Guardado encoder_years en: {path}")
    else:
        print("Warning: columna 'Years in Business Band' no encontrada en el CSV")

    print('\nListo. Copia los archivos bajo', out_dir, 'al servidor de producción (artifacts/).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Genera y guarda encoders ordinales desde CSV de entrenamiento')
    parser.add_argument('--input', '-i', required=True, help='Ruta al CSV (ej: df_company_tot.csv)')
    parser.add_argument('--out', '-o', default='artifacts', help='Directorio de salida para encoders')
    args = parser.parse_args()
    main(args.input, args.out)
