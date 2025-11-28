from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a la base de datos PostgreSQL.
# Formato: "postgresql://usuario:contraseña@host:puerto/nombre_db"
# TODO: Mover esto a variables de entorno o un archivo de configuración.
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/partner_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()