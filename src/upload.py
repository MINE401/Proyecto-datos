from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional

import pandas as pd

from db import supabase
from controllers.location import prepare_location_data
from controllers.industry import prepare_industry_data
from controllers.general import (
    prepare_score_data,
    prepare_cloud_data,
    prepare_partner_class_data,
    prepare_technology_sc_data,
    prepare_technology_data,
    prepare_partner_vendor_data,
)

BASE_DATA_DIR = Path("src/data")


def _read_csv(file_name: str) -> pd.DataFrame:
    """Lee un CSV desde el directorio de datos y muestra sus columnas."""
    file_path = BASE_DATA_DIR / file_name
    df = pd.read_csv(file_path)
    print(f"Columnas del CSV {file_name}:", df.columns.tolist())
    return df


def upload_data(
    file_name: str,
    table_name: str,
    chunk_size: int = 1000,
    column_map: Optional[Mapping[str, str]] = None,
    keep_columns: Optional[Iterable[str]] = None,
    required_not_null: Optional[Iterable[str]] = None,
    default_values: Optional[Mapping[str, object]] = None,
) -> None:
    """Sube datos de un CSV a una tabla de Supabase en chunks."""
    df = _read_csv(file_name)

    if column_map:
        df = df.rename(columns=column_map)

    if keep_columns:
        keep_columns = [col for col in keep_columns if col in df.columns]
        df = df[list(keep_columns)]

    if default_values:
        for col, default in default_values.items():
            if col in df.columns:
                before = df[col].isnull().sum()
                df[col] = df[col].fillna(default)
                after = df[col].isnull().sum()
                filled = before - after
                if filled > 0:
                    print(
                        f"Se llenaron {filled} valores nulos en '{col}' con '{default}'"
                    )

    if required_not_null:
        for col in required_not_null:
            if col not in df.columns:
                print(
                    f"Advertencia: la columna requerida '{col}' no existe en el CSV. Se omite esta validacion."
                )
                continue
            before = len(df)
            df = df[df[col].notnull()]
            removed = before - len(df)
            if removed > 0:
                print(f"Se eliminaron {removed} filas con '{col}' nulo")

    df = df.where(pd.notnull(df), None)

    records: List[Dict[str, object]] = df.to_dict(orient="records")
    total = len(records)
    print(f"Subiendo {total} filas a la tabla '{table_name}'...")

    for i in range(0, total, chunk_size):
        chunk = records[i : i + chunk_size]
        resp = supabase.table(table_name).insert(chunk).execute()

        if getattr(resp, "error", None):
            print(f"Error en el chunk {i // chunk_size + 1}: {resp.error}")
            break

    print(f"Subida a '{table_name}' finalizada.")


def upload_company() -> None:
    upload_data(
        file_name="df_company_tot.csv",
        table_name="company",
        column_map={
            "Company ID": "external_company_id",
            "name": "name",
            "Website": "website",
            "Number of Locations Band": "num_locations_bands",
            "Years in Business Band": "year_business_back",
            "Employee Band": "employee_band",
            "Revenue Band": "revenue_band",
        },
        keep_columns=[
            "external_company_id",
            "name",
            "website",
            "num_locations_bands",
            "year_business_back",
            "employee_band",
            "revenue_band",
        ],
        default_values={"name": "No Name"},
        required_not_null=None,
    )


def upload_location_master() -> None:
    upload_data(
        file_name="location_master.csv",
        table_name="location_master",
        keep_columns=[
            "id",
            "global_region",
            "region",
            "country",
            "state",
            "city",
        ],
    )


def upload_company_location() -> None:
    upload_data(
        file_name="company_location.csv",
        table_name="company_location",
        keep_columns=[
            "company_id",
            "location_id",
            "address_type",
        ],
    )


def upload_industry_master() -> None:
    upload_data(
        file_name="industry_master.csv",
        table_name="industry_master",
        keep_columns=[
            "id",
            "sector",
            "detail",
        ],
    )


def upload_score() -> None:
    upload_data(
        file_name="score_ready.csv",
        table_name="score",
        keep_columns=[
            "company_id",
            "relevance",
        ],
    )


def upload_company_industry() -> None:
    upload_data(
        file_name="company_industry.csv",
        table_name="company_industry",
        keep_columns=[
            "company_id",
            "industry_id",
        ],
    )


def upload_cloud() -> None:
    upload_data(
        file_name="cloud_ready.csv",
        table_name="cloud",
        keep_columns=[
            "company_id",
            "coverage",
        ],
    )


def upload_partner_classification() -> None:
    upload_data(
        file_name="partner_classification_ready.csv",
        table_name="partner_classification",
        keep_columns=[
            "company_id",
            "classification",
        ],
    )


def upload_technology_sc() -> None:
    upload_data(
        file_name="technology_sc_ready.csv",
        table_name="technology_sc",
        keep_columns=[
            "company_id",
            "scope",
        ],
    )


def upload_technology() -> None:
    upload_data(
        file_name="technology_ready.csv",
        table_name="technology",
        keep_columns=[
            "company_id",
            "tech_group",
            "technology",
            "detail",
            "category",
        ],
    )


def upload_partner_vendor() -> None:
    upload_data(
        file_name="partner_vendor_ready.csv",
        table_name="partner_vendor",
        keep_columns=[
            "partner_id",
            "vendor_id",
        ],
    )


if __name__ == "__main__":
    print("====== INICIANDO CARGA DE DATOS ======\n")

    upload_company()

    prepare_location_data()
    upload_location_master()
    upload_company_location()

    prepare_industry_data()
    upload_industry_master()
    upload_company_industry()

    prepare_score_data()
    upload_score()

    prepare_cloud_data()
    upload_cloud()

    prepare_partner_class_data()
    upload_partner_classification()

    prepare_technology_sc_data()
    upload_technology_sc()

    prepare_technology_data()
    upload_technology()

    prepare_partner_vendor_data()
    upload_partner_vendor()

    print("TODAS LAS CARGAS TERMINADAS")
