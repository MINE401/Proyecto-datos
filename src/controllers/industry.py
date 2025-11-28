import uuid
import pandas as pd
from db import supabase


def prepare_industry_data():
    # 1) Leer CSV original
    df = pd.read_csv("src/data/df_industry_filtered.csv")

    df = df.rename(columns={
        "Company ID": "external_company_id",
        "Sector (Customer)": "sector",
        "Industry Detail (Customer)": "detail",
    })

    ind_cols = ["sector", "detail"]

    # ===================================================
    # 2) INDUSTRY_MASTER (con UNKNOWN)
    # ===================================================
    df_ind_master = df[ind_cols].drop_duplicates().reset_index(drop=True)

    unknown_row = {"sector": "UNKNOWN", "detail": "UNKNOWN"}
    df_unknown = pd.DataFrame([unknown_row])
    df_ind_master = pd.concat([df_ind_master, df_unknown], ignore_index=True)

    df_ind_master["id"] = [str(uuid.uuid4()) for _ in range(len(df_ind_master))]
    df_ind_master = df_ind_master[["id"] + ind_cols]

    df_ind_master.to_csv("src/data/industry_master.csv", index=False)
    print(f"industry_master.csv generado con {len(df_ind_master)} filas")

    # ID de la industria UNKNOWN
    unknown_id = df_ind_master[df_ind_master["sector"] == "UNKNOWN"].iloc[0]["id"]

    # ===================================================
    # 3) MAPEO COMPANY (external_company_id -> uuid)
    # ===================================================
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    # todos los company_id reales
    all_company_ids = [row["id"] for row in company_rows]

    mapping_ext_to_uuid = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    # ===================================================
    # 4) COMPANY_INDUSTRY desde el CSV
    # ===================================================
    df_merged = df.merge(df_ind_master, on=ind_cols, how="left")

    df_merged["company_id"] = df_merged["external_company_id"].map(mapping_ext_to_uuid)
    df_merged["industry_id"] = df_merged["id"]

    df_company_industry = df_merged[["company_id", "industry_id"]]

    # quitar filas sin company_id (Company ID que no están en company)
    before = len(df_company_industry)
    df_company_industry = df_company_industry.dropna(subset=["company_id", "industry_id"])
    removed = before - len(df_company_industry)
    if removed > 0:
        print(f"⚠️ {removed} filas descartadas por no encontrar company_id o industry_id")

    # ===================================================
    # 5) ASIGNAR UNKNOWN A COMPAÑÍAS SIN INDUSTRIA
    # ===================================================
    used_company_ids = set(df_company_industry["company_id"].unique())
    missing_company_ids = [cid for cid in all_company_ids if cid not in used_company_ids]

    if missing_company_ids:
        df_missing = pd.DataFrame({
            "company_id": missing_company_ids,
            "industry_id": [unknown_id] * len(missing_company_ids),
        })
        df_company_industry = pd.concat([df_company_industry, df_missing], ignore_index=True)
        print(f"✅ Se asignó industry UNKNOWN a {len(missing_company_ids)} compañías sin industria")

    # eliminar duplicados (misma company, misma industry)
    df_company_industry = df_company_industry.drop_duplicates().reset_index(drop=True)

    df_company_industry.to_csv("src/data/company_industry.csv", index=False)
    print(f"company_industry.csv generado con {len(df_company_industry)} filas")
