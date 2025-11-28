from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from fastapi.middleware.cors import CORSMiddleware

import crud
import models
import schemas
from database import SessionLocal, engine, get_db

# Crea las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Consulta de Compañías",
    description="Un endpoint para realizar consultas complejas a la base de datos."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/query", response_model=List[Dict[str, Any]])
async def handle_query(
    # Usamos Body(..., discriminator="action") para ayudar a FastAPI
    # con la Unión Discriminada.
    query: schemas.QueryRequest = Body(..., discriminator="action"),
    db: Session = Depends(get_db) # Inyectar la sesión de la DB
):
    """
    Endpoint unificado para consultar la base de datos.

    - **list_companies**: Lista todas las compañías con paginación y ordenamiento.
    - **list_territories**: Lista valores únicos de un campo de territorio.
    - **search_company**: Busca compañías por territorio y/o nombre de cliente.
    """
    if query.action == "list_companies":
        # Llama a la función CRUD correspondiente
        return crud.list_companies(db=db, params=query.params, pagination=query.pagination)

    if query.action == "list_territories":
        return crud.list_territories(db=db, params=query.params)

    if query.action == "search_company":
        # Validar que al menos un criterio de búsqueda fue provisto
        if not query.params.territory and not query.params.client_name:
            raise HTTPException(
                status_code=422,
                detail="Para 'search_company', se requiere 'territory' o 'clientName'."
            )
        return crud.search_companies(db=db, params=query.params, pagination=query.pagination)

    # Este caso no debería ocurrir gracias a la validación de Pydantic
    raise HTTPException(status_code=400, detail="Acción no válida.")