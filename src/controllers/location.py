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


def prepare_location_data() -> None:
    """Prepara datos de ubicaciones para las tablas location_master y company_location."""
    df = _read_csv("df_location_filtered.csv")

    df = df.rename(
        columns={
            "Company ID": "external_company_id",
            "Global Region": "global_region",
            "Region": "region",
            "Country": "country",
            "State/Province": "state",
            "City": "city",
            "Address Type": "address_type",
        }
    )

    loc_cols = ["global_region", "region", "country", "state", "city"]

    df_loc_master = df[loc_cols].drop_duplicates().reset_index(drop=True)

    unknown_row = {
        "global_region": "UNKNOWN",
        "region": "UNKNOWN",
        "country": "UNKNOWN",
        "state": "UNKNOWN",
        "city": "UNKNOWN",
    }

    df_loc_master = pd.concat(
        [df_loc_master, pd.DataFrame([unknown_row])], ignore_index=True
    )

    df_loc_master["id"] = [str(uuid.uuid4()) for _ in range(len(df_loc_master))]
    df_loc_master = df_loc_master[["id"] + loc_cols]

    location_master_path = BASE_DATA_DIR / "location_master.csv"
    df_loc_master.to_csv(location_master_path, index=False)
    print(f"location_master.csv generado con {len(df_loc_master)} filas")

    unknown_id = df_loc_master[df_loc_master["country"] == "UNKNOWN"].iloc[0]["id"]

    mapping_ext_to_uuid, all_company_ids = _get_company_mapping()

    df_merged = df.merge(df_loc_master, on=loc_cols, how="left")
    df_merged["company_id"] = df_merged["external_company_id"].map(
        mapping_ext_to_uuid
    )

    df_merged["location_id"] = df_merged["id"].fillna(unknown_id)

    df_company_location = df_merged[["company_id", "location_id", "address_type"]]
    df_company_location = df_company_location.dropna(subset=["company_id"])

    used_company_ids = set(df_company_location["company_id"].unique())
    missing_company_ids = [cid for cid in all_company_ids if cid not in used_company_ids]

    if missing_company_ids:
        df_missing = pd.DataFrame(
            {
                "company_id": missing_company_ids,
                "location_id": [unknown_id] * len(missing_company_ids),
                "address_type": ["UNKNOWN"] * len(missing_company_ids),
            }
        )
        df_company_location = pd.concat(
            [df_company_location, df_missing], ignore_index=True
        )
        print(
            f"Se asigno location UNKNOWN a {len(missing_company_ids)} companias sin ubicacion"
        )

    df_company_location = df_company_location.drop_duplicates().reset_index(drop=True)

    company_location_path = BASE_DATA_DIR / "company_location.csv"
    df_company_location.to_csv(company_location_path, index=False)
    print(f"company_location.csv generado con {len(df_company_location)} filas")
