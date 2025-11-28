# /Users/juank1400/workspaces/mati/MINE-Proyecto/app/schemas.py

from pydantic import BaseModel, Field, conint
from typing import Literal, Optional, Union, List

# --- Modelos para los parámetros de cada acción ---

class ListCompaniesParams(BaseModel):
    sort_by: Literal["name", "relevance_score"] = "name"
    sort_order: Literal["asc", "desc"] = "asc"

class ListTerritoriesParams(BaseModel):
    filter_by: Literal["country", "region", "global_region"]

class TerritoryFilter(BaseModel):
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None

class SearchCompanyParams(BaseModel):
    territory: Optional[TerritoryFilter] = None
    client_name: Optional[str] = Field(None, alias="clientName")

    # Pydantic no tiene un análogo directo para "anyOf" en este contexto,
    # pero podemos validarlo en el endpoint o con un validador personalizado si es necesario.
    # Por ahora, ambos son opcionales y la lógica de negocio lo manejará.

class Pagination(BaseModel):
    limit: conint(ge=1) = 20
    offset: conint(ge=0) = 0

# --- Modelos base para cada tipo de solicitud (Unión Discriminada) ---

class BaseQuery(BaseModel):
    pagination: Optional[Pagination] = Field(default_factory=Pagination)
    
    class Config:
        # Permite usar alias como "clientName" en el JSON y "client_name" en el modelo
        allow_population_by_field_name = True

class ListCompaniesQuery(BaseQuery):
    action: Literal["list_companies"]
    params: Optional[ListCompaniesParams] = Field(default_factory=ListCompaniesParams)

class ListTerritoriesQuery(BaseQuery):
    action: Literal["list_territories"]
    params: ListTerritoriesParams

class SearchCompanyQuery(BaseQuery):
    action: Literal["search_company"]
    params: SearchCompanyParams

# --- El modelo de Unión que el endpoint aceptará ---

QueryRequest = Union[ListCompaniesQuery, ListTerritoriesQuery, SearchCompanyQuery]

# Modelo de respuesta genérico (ejemplo)
class Company(BaseModel):
    id: int
    name: str
    # ... otros campos de la compañía

    class Config:
        orm_mode = True # En Pydantic v2, se usa from_attributes = True

