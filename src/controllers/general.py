import pandas as pd
from db import supabase


def prepare_score_data():
    df = pd.read_csv("src/data/df_score.csv")

    # Renombrar columnas necesarias
    df = df.rename(columns={
        "Company ID": "external_company_id",
        "Relevance": "relevance",
        "Vendors": "vendors",
        "Partner Classification": "partner_classification",
    })

    # Solo dejamos las columnas que interesan
    df = df[
        [
            "external_company_id",
            "relevance",
            "vendors",
            "partner_classification",
        ]
    ]

    # Traer mapping external_company_id -> company.id (UUID)
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    mapping = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    # Mapear a company_id real
    df["company_id"] = df["external_company_id"].map(mapping)

    # Eliminar filas sin company_id
    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(f" {removed} filas de score descartadas por no encontrar company_id")

    # Quitar external_company_id antes de subir
    df = df.drop(columns=["external_company_id"])

    # Guardar CSV final
    df.to_csv("src/data/score_ready.csv", index=False)
    print(f"score_ready.csv generado con {len(df)} filas")


def prepare_score_data():

    df = pd.read_csv("src/data/df_score.csv")
    print("Columnas df_score:", df.columns.tolist())

    # 1) Detectar la columna de "Partner Classification" aunque tenga texto extra
    partner_col = None
    for col in df.columns:
        if col.strip().startswith("Partner Classification"):
            partner_col = col
            break

    # 2) Armar el mapa de renombrado
    rename_map = {
        "Company ID": "external_company_id",
        "Relevance": "relevance",
        "Vendors": "vendors",
    }
    if partner_col is not None:
        rename_map[partner_col] = "partner_classification"

    df = df.rename(columns=rename_map)

    # 3) Elegir columnas a conservar
    keep_cols = ["external_company_id", "relevance", "vendors"]
    if "partner_classification" in df.columns:
        keep_cols.append("partner_classification")
    else:
        # si no existe, la creamos con None
        df["partner_classification"] = None
        keep_cols.append("partner_classification")

    df = df[keep_cols]

    # 4) Traer mapping external_company_id -> company.id (uuid real)
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    mapping = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    df["company_id"] = df["external_company_id"].map(mapping)

    # 5) Filtrar filas cuyo Company ID no existe en company
    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(f" {removed} filas de score descartadas por no encontrar company_id en 'company'")

    # 6) Quitar external_company_id y guardar CSV listo para subir
    df = df.drop(columns=["external_company_id"])

    df.to_csv("src/data/score_ready.csv", index=False)
    print(f" score_ready.csv generado con {len(df)} filas")


def prepare_cloud_data():
    df = pd.read_csv("src/data/df_cloud_filtered.csv")
    print("Columnas df_cloud:", df.columns.tolist())

    # Renombrar columnas
    df = df.rename(columns={
        "Company ID": "external_company_id",
        "Cloud Coverage": "coverage",
    })

    # Tratar '-' como sin dato (None)
    df["coverage"] = df["coverage"].replace("-", None)

    # Traer mapping external_company_id -> company.id (uuid)
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    mapping = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    # Mapear a company_id real
    df["company_id"] = df["external_company_id"].map(mapping)

    # Filtrar filas cuyo Company ID no existe en company
    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(f" {removed} filas de cloud descartadas por no encontrar company_id en 'company'")

    # Nos quedamos solo con las columnas que va a usar la tabla cloud
    df = df[["company_id", "coverage"]]

    # Guardar CSV listo para subir
    df.to_csv("src/data/cloud_ready.csv", index=False)
    print(f" cloud_ready.csv generado con {len(df)} filas")

def prepare_partner_class_data():
    df = pd.read_csv("src/data/df_partners_class_filtered.csv")
    print("Columnas df_partners_class:", df.columns.tolist())

    # 1) Detectar la columna de clasificación de partner
    class_col = None
    for col in df.columns:
        if col.strip().startswith("Partner Class"):
            class_col = col
            break

    if class_col is None:
        raise ValueError("No se encontró ninguna columna que empiece por 'Partner Class'")

    # 2) Renombrar columnas
    df = df.rename(columns={
        "Company ID": "external_company_id",
        class_col: "classification",
    })

    # 3) Nos quedamos con lo que importa
    df = df[["external_company_id", "classification"]]

    # 4) Mapear external_company_id -> company.id (uuid real)
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    mapping = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    df["company_id"] = df["external_company_id"].map(mapping)

    # 5) Filtrar filas cuyo Company ID no existe en company
    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(f"⚠️ {removed} filas de partner_classification descartadas por no encontrar company_id en 'company'")

    # 6) Quitar external_company_id y quitar duplicados
    df = df.drop(columns=["external_company_id"])
    df = df.drop_duplicates().reset_index(drop=True)

    # 7) Guardar CSV listo para subir
    df.to_csv("src/data/partner_classification_ready.csv", index=False)
    print(f" partner_classification_ready.csv generado con {len(df)} filas")


def prepare_technology_sc_data():
    df = pd.read_csv("src/data/df_technology_sc_filtered.csv")
    print("Columnas df_technology_sc:", df.columns.tolist())

    # Renombrar columnas
    df = df.rename(columns={
        "Company ID": "external_company_id",
        "Technology Scope": "scope",
    })

    # Limpiar valores vacíos o '-'
    df["scope"] = df["scope"].replace("-", None)

    # Traer mapping external_company_id -> company.id (uuid)
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    mapping = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    # Mapear a company_id real
    df["company_id"] = df["external_company_id"].map(mapping)

    # Filtrar filas cuyo Company ID no existe en company
    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(f" {removed} filas de technology_sc descartadas por no encontrar company_id")

    # Nos quedamos solo con las columnas que va a usar la tabla
    df = df[["company_id", "scope"]]

    # Quitar duplicados (misma company + mismo scope)
    df = df.drop_duplicates().reset_index(drop=True)

    # Guardar CSV listo para subir
    df.to_csv("src/data/technology_sc_ready.csv", index=False)
    print(f" technology_sc_ready.csv generado con {len(df)} filas")


def prepare_technology_data():
    df = pd.read_csv("src/data/df_technology.csv")
    print("Columnas df_technology:", df.columns.tolist())

    # 1. Renombrar columnas según la tabla destino
    df = df.rename(columns={
        "Company ID": "external_company_id",
        "Technology Group": "tech_group",
        "Technology": "technology",
        "Technology Detail": "detail",
        "Technology Category": "category",
    })

    # 2. Nos quedamos solo con las columnas necesarias
    df = df[
        ["external_company_id", "tech_group", "technology", "detail", "category"]
    ]

    # 3. Limpieza básica
    df = df.replace("-", None)
    df = df.where(pd.notnull(df), None)

    # 4. Obtener relación external_company_id → company.id (UUID real)
    resp = supabase.table("company").select("id, external_company_id").execute()
    company_rows = resp.data

    mapping = {
        row["external_company_id"]: row["id"]
        for row in company_rows
        if row["external_company_id"] is not None
    }

    # 5. Mapear company_id real
    df["company_id"] = df["external_company_id"].map(mapping)

    # 6. Filtrar compañías que no existan en company
    before = len(df)
    df = df[df["company_id"].notnull()]
    removed = before - len(df)
    if removed > 0:
        print(f"⚠️ {removed} filas de technology descartadas por company_id inexistente")

    # 7. Quitar external_company_id
    df = df.drop(columns=["external_company_id"])

    # 8. Quitar duplicados exactos
    df = df.drop_duplicates().reset_index(drop=True)

    # 9. Guardar archivo listo
    df.to_csv("src/data/technology_ready.csv", index=False)
    print(f" technology_ready.csv generado con {len(df)} filas")

def prepare_partner_vendor_data():
    df = pd.read_csv("src/data/df_partners_vendors.csv")
    print("Columnas df_partners_vendors:", df.columns.tolist())

    # Renombrar columnas
    df = df.rename(columns={
        "Company ID (Partner)": "external_partner_id",
        "Company ID (Vendor)": "external_vendor_id",
    })

    df = df[
        ["external_partner_id", "external_vendor_id"]
    ]

    # Traer mapping external_company_id -> uuid real
    resp = supabase.table("company").select("id, external_company_id").execute()
    rows = resp.data

    mapping = {
        r["external_company_id"]: r["id"]
        for r in rows
        if r["external_company_id"] is not None
    }

    # Mapear UUIDs reales
    df["partner_id"] = df["external_partner_id"].map(mapping)
    df["vendor_id"] = df["external_vendor_id"].map(mapping)

    # Filtrar los que no existan en company
    before = len(df)
    df = df[
        df["partner_id"].notnull() &
        df["vendor_id"].notnull()
    ]
    removed = before - len(df)

    if removed > 0:
        print(f" {removed} relaciones partner-vendor descartadas por company_id inexistente")

    # Nos quedamos solo con los IDs finales
    df = df[["partner_id", "vendor_id"]]

    # Quitar duplicados
    df = df.drop_duplicates().reset_index(drop=True)

    # Guardar listo para subir
    df.to_csv("src/data/partner_vendor_ready.csv", index=False)
    print(f" partner_vendor_ready.csv generado con {len(df)} filas")