from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from db import supabase

BASE_DATA_DIR = Path("src/data")


def _read_csv(file_name: str) -> pd.DataFrame:
    """Lee un CSV desde el directorio de datos."""
    file_path = BASE_DATA_DIR / file_name
    return pd.read_csv(file_path)


def _get_company_mapping() -> Tuple[Dict[str, str], List[str]]:
    """Obtiene el mapeo external_company_id -> company.id y la lista de ids."""
    resp = supabase.table("company").select("id, external_company_id").execute()
    rows = getattr(resp, "data", []) or []
    ids = [row["id"] for row in rows]
    mapping = {
        row["external_company_id"]: row["id"]
        for row in rows
        if row.get("external_company_id") is not None
    }
    return mapping, ids


def prepare_score_data() -> None:
    """Prepara datos de score para la tabla score."""
    df = _read_csv("df_score.csv")
    print("Columnas df_score:", df.columns.tolist())

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            "Relevance": "relevance",
        }
    )

    df = df[["external_company_id", "relevance"]]

    df = df.replace("-", None)
    df = df.where(pd.notnull(df), None)

    mapping, _ = _get_company_mapping()
    df["company_id"] = df["external_company_id"].map(mapping)

    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(
            f"{removed} filas de score descartadas por no encontrar company_id en 'company'"
        )

    df = df.drop(columns=["external_company_id"])
    df = df.drop_duplicates().reset_index(drop=True)

    output_path = BASE_DATA_DIR / "score_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"score_ready.csv generado con {len(df)} filas")


def prepare_cloud_data() -> None:
    """Prepara datos de cloud para la tabla cloud."""
    df = _read_csv("df_cloud_filtered.csv")
    print("Columnas df_cloud:", df.columns.tolist())

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            "Cloud Coverage": "coverage",
        }
    )

    df["coverage"] = df["coverage"].replace("-", None)

    mapping, _ = _get_company_mapping()
    df["company_id"] = df["external_company_id"].map(mapping)

    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(
            f"{removed} filas de cloud descartadas por no encontrar company_id en 'company'"
        )

    df = df[["company_id", "coverage"]]

    output_path = BASE_DATA_DIR / "cloud_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"cloud_ready.csv generado con {len(df)} filas")


def prepare_partner_class_data() -> None:
    """Prepara datos de clasificación de partners para la tabla partner_classification."""
    df = _read_csv("df_partners_class_filtered.csv")
    print("Columnas df_partners_class:", df.columns.tolist())

    class_col = None
    for col in df.columns:
        if col.strip().startswith("Partner Class"):
            class_col = col
            break

    if class_col is None:
        raise ValueError(
            "No se encontró ninguna columna que empiece por 'Partner Class'"
        )

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            class_col: "classification",
        }
    )

    df = df[["external_company_id", "classification"]]

    mapping, _ = _get_company_mapping()
    df["company_id"] = df["external_company_id"].map(mapping)

    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(
            f"{removed} filas de partner_classification descartadas por no encontrar company_id en 'company'"
        )

    df = df.drop(columns=["external_company_id"])
    df = df.drop_duplicates().reset_index(drop=True)

    output_path = BASE_DATA_DIR / "partner_classification_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"partner_classification_ready.csv generado con {len(df)} filas")


def prepare_technology_sc_data() -> None:
    """Prepara datos de technology scope para la tabla technology_sc."""
    df = _read_csv("df_technology_sc_filtered.csv")
    print("Columnas df_technology_sc:", df.columns.tolist())

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            "Technology Scope": "scope",
        }
    )

    df["scope"] = df["scope"].replace("-", None)

    mapping, _ = _get_company_mapping()
    df["company_id"] = df["external_company_id"].map(mapping)

    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(
            f"{removed} filas de technology_sc descartadas por no encontrar company_id en 'company'"
        )

    df = df[["company_id", "scope"]]
    df = df.drop_duplicates().reset_index(drop=True)

    output_path = BASE_DATA_DIR / "technology_sc_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"technology_sc_ready.csv generado con {len(df)} filas")


def prepare_technology_data() -> None:
    """Prepara datos de tecnología para la tabla technology."""
    df = _read_csv("df_technology.csv")
    print("Columnas df_technology:", df.columns.tolist())

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            "Technology Group": "tech_group",
            "Technology": "technology",
            "Technology Detail": "detail",
            "Technology Category": "category",
        }
    )

    df = df[
        ["external_company_id", "tech_group", "technology", "detail", "category"]
    ]

    df = df.replace("-", None)
    df = df.where(pd.notnull(df), None)

    mapping, _ = _get_company_mapping()
    df["company_id"] = df["external_company_id"].map(mapping)

    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(
            f"{removed} filas de technology descartadas por no encontrar company_id en 'company'"
        )

    df = df.drop(columns=["external_company_id"])
    df = df.drop_duplicates().reset_index(drop=True)

    output_path = BASE_DATA_DIR / "technology_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"technology_ready.csv generado con {len(df)} filas")


def prepare_partner_vendor_data() -> None:
    """Prepara relaciones partner-vendor para la tabla partner_vendor."""
    df = _read_csv("df_partners_vendors.csv")
    print("Columnas df_partners_vendors:", df.columns.tolist())

    df = df.rename(
        columns={
            "Company ID (Partner)": "external_partner_id",
            "Company ID (Vendor)": "external_vendor_id",
        }
    )

    df = df[["external_partner_id", "external_vendor_id"]]

    mapping, _ = _get_company_mapping()

    df["partner_id"] = df["external_partner_id"].map(mapping)
    df["vendor_id"] = df["external_vendor_id"].map(mapping)

    before = len(df)
    df = df[df["partner_id"].notnull() & df["vendor_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(
            f"{removed} relaciones partner-vendor descartadas por company_id inexistente"
        )

    df = df[["partner_id", "vendor_id"]]
    df = df.drop_duplicates().reset_index(drop=True)

    output_path = BASE_DATA_DIR / "partner_vendor_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"partner_vendor_ready.csv generado con {len(df)} filas")
