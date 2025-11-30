import uuid
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


def prepare_industry_data() -> None:
    """Prepara datos de industrias para las tablas industry_master y company_industry."""
    df = _read_csv("df_industry_filtered.csv")

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            "Sector (Customer)": "sector",
            "Industry Detail (Customer)": "detail",
        }
    )

    ind_cols = ["sector", "detail"]

    df_ind_master = df[ind_cols].drop_duplicates().reset_index(drop=True)

    unknown_row = {"sector": "UNKNOWN", "detail": "UNKNOWN"}
    df_unknown = pd.DataFrame([unknown_row])
    df_ind_master = pd.concat([df_ind_master, df_unknown], ignore_index=True)

    df_ind_master["id"] = [str(uuid.uuid4()) for _ in range(len(df_ind_master))]
    df_ind_master = df_ind_master[["id"] + ind_cols]

    industry_master_path = BASE_DATA_DIR / "industry_master.csv"
    df_ind_master.to_csv(industry_master_path, index=False)
    print(f"industry_master.csv generado con {len(df_ind_master)} filas")

    unknown_id = df_ind_master[df_ind_master["sector"] == "UNKNOWN"].iloc[0]["id"]

    mapping_ext_to_uuid, all_company_ids = _get_company_mapping()

    df_merged = df.merge(df_ind_master, on=ind_cols, how="left")

    df_merged["company_id"] = df_merged["external_company_id"].map(
        mapping_ext_to_uuid
    )
    df_merged["industry_id"] = df_merged["id"]

    df_company_industry = df_merged[["company_id", "industry_id"]]

    before = len(df_company_industry)
    df_company_industry = df_company_industry.dropna(
        subset=["company_id", "industry_id"]
    )
    removed = before - len(df_company_industry)
    if removed > 0:
        print(
            f"{removed} filas descartadas por no encontrar company_id o industry_id"
        )

    used_company_ids = set(df_company_industry["company_id"].unique())
    missing_company_ids = [cid for cid in all_company_ids if cid not in used_company_ids]

    if missing_company_ids:
        df_missing = pd.DataFrame(
            {
                "company_id": missing_company_ids,
                "industry_id": [unknown_id] * len(missing_company_ids),
            }
        )
        df_company_industry = pd.concat(
            [df_company_industry, df_missing], ignore_index=True
        )
        print(
            f"Se asigno industry UNKNOWN a {len(missing_company_ids)} companias sin industria"
        )

    df_company_industry = df_company_industry.drop_duplicates().reset_index(drop=True)

    company_industry_path = BASE_DATA_DIR / "company_industry.csv"
    df_company_industry.to_csv(company_industry_path, index=False)
    print(f"company_industry.csv generado con {len(df_company_industry)} filas")
