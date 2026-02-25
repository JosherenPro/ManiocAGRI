from sqlmodel import create_engine, Session, SQLModel
from core.config import settings
from sqlalchemy.pool import NullPool

# Utilisation du Transaction Pooler (port 6543) : on gère déjà le pooling côté serveur (PgBouncer)
# Il est fortement recommandé de désactiver le pool SQLAlchemy (NullPool) pour éviter les deadlocks
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
