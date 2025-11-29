import uuid
import pandas as pd
from db import supabase


def prepare_location_data():
    # 1) Leer CSV original de locaciones
    df = pd.read_csv("src/data/df_location_filtered.csv")

    df = df.rename(columns={
        "Company ID": "external_company_id",
        "Global Region": "global_region",
        "Region": "region",
        "Country": "country",
        "State/Province": "state",
        "City": "city",
        "Address Type": "address_type",
    })

    loc_cols = ["global_region", "region", "country", "state", "city"]

    # ===================================================
    # 2) LOCATION_MASTER (con fila UNKNOWN)
    # ===================================================
    # ubicaciones reales
    df_loc_master = df[loc_cols].drop_duplicates().reset_index(drop=True)

    # fila UNKNOWN
    unknown_row = {
        "global_region": "UNKNOWN",
        "region": "UNKNOWN",
        "country": "UNKNOWN",
        "state": "UNKNOWN",
        "city": "UNKNOWN",
    }

    df_loc_master = pd.concat(
        [df_loc_master, pd.DataFrame([unknown_row])],
        ignore_index=True
    )

    # asignar UUID a cada ubicación
    df_loc_master["id"] = [str(uuid.uuid4()) for _ in range(len(df_loc_master))]
    df_loc_master = df_loc_master[["id"] + loc_cols]

    df_loc_master.to_csv("src/data/location_master.csv", index=False)
    print(f"location_master.csv generado con {len(df_loc_master)} filas")

    # id de la ubicación UNKNOWN
    unknown_id = df_loc_master[df_loc_master["country"] == "UNKNOWN"].iloc[0]["id"]

    # ===================================================
    # 3) MAPEO COMPANY (external_company_id -> uuid real)
    # ===================================================
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    all_company_ids = [row["id"] for row in company_rows]

    mapping_ext_to_uuid = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    # ===================================================
    # 4) COMPANY_LOCATION a partir del CSV
    # ===================================================
    df_merged = df.merge(df_loc_master, on=loc_cols, how="left")

    df_merged["company_id"] = df_merged["external_company_id"].map(mapping_ext_to_uuid)

    # si por algún motivo una ubicación no se encontró, se manda a UNKNOWN
    df_merged["location_id"] = df_merged["id"].fillna(unknown_id)

    df_company_location = df_merged[["company_id", "location_id", "address_type"]]

    # quitar filas sin company_id (Company ID que no existen en company)
    df_company_location = df_company_location.dropna(subset=["company_id"])

    # ===================================================
    # 5) ASIGNAR LOCATION UNKNOWN A COMPAÑÍAS SIN FILAS EN EL CSV
    # ===================================================
    used_company_ids = set(df_company_location["company_id"].unique())
    missing_company_ids = [cid for cid in all_company_ids if cid not in used_company_ids]

    if missing_company_ids:
        df_missing = pd.DataFrame({
            "company_id": missing_company_ids,
            "location_id": [unknown_id] * len(missing_company_ids),
            "address_type": ["UNKNOWN"] * len(missing_company_ids),
        })
        df_company_location = pd.concat([df_company_location, df_missing], ignore_index=True)
        print(f"✅ Se asignó location UNKNOWN a {len(missing_company_ids)} compañías sin ubicación")

    # quitar duplicados (misma company + misma location)
    df_company_location = df_company_location.drop_duplicates().reset_index(drop=True)

    df_company_location.to_csv("src/data/company_location.csv", index=False)
    print(f"company_location.csv generado con {len(df_company_location)} filas")
