from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc
import models
import schemas

def list_companies(db: Session, params: schemas.ListCompaniesParams, pagination: schemas.Pagination):
    """
    Obtiene una lista de compañías con ordenamiento y paginación.
    """
    query = db.query(models.Company)

    # Aplicar ordenamiento
    if params.sort_by == "name":
        order_column = models.Company.name
    elif params.sort_by == "relevance_score":
        # Asumiendo que el relevance_score está en la tabla Score
        query = query.join(models.Score)
        order_column = models.Score.relevance
    else:
        order_column = models.Company.name # Default

    if params.sort_order == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(order_column)

    # Aplicar paginación
    companies = query.offset(pagination.offset).limit(pagination.limit).all()
    return companies

def list_territories(db: Session, params: schemas.ListTerritoriesParams):
    """
    Obtiene una lista de valores únicos para un campo de territorio.
    """
    field_to_query = getattr(models.Location, params.filter_by)
    
    results = db.query(field_to_query).distinct().all()
    
    # Los resultados son tuplas, los convertimos a una lista de diccionarios
    return [{params.filter_by: value} for value, in results if value]

def search_companies(db: Session, params: schemas.SearchCompanyParams, pagination: schemas.Pagination):
    """
    Busca compañías basadas en filtros de territorio y/o nombre de cliente.
    """
    query = db.query(models.Company)

    # Filtrar por territorio
    if params.territory:
        query = query.join(models.Location)
        territory_filters = params.territory.dict(exclude_unset=True)
        for field, value in territory_filters.items():
            if hasattr(models.Location, field):
                query = query.filter(getattr(models.Location, field).ilike(f"%{value}%"))

    # Filtrar por nombre de cliente (busca partners de un cliente específico)
    if params.client_name:
        # Creamos un alias para la tabla Company para representar al "cliente"
        ClientCompany = aliased(models.Company)
        
        # Unimos Company (partner) -> partner_vendor (asociación) -> Company (cliente)
        query = query.join(models.partner_vendor_association, models.Company.id == models.partner_vendor_association.c.partner_id)\
                     .join(ClientCompany, ClientCompany.id == models.partner_vendor_association.c.vendor_id)\
                     .filter(ClientCompany.name.ilike(f"%{params.client_name}%"))

    # Aplicar paginación
    companies = query.offset(pagination.offset).limit(pagination.limit).all()
    return companies