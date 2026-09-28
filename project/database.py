from sqlmodel import SQLModel, create_engine, Session

# El engine es la conexión "de bajo nivel" a la base de datos.
# Acá usamos SQLite, que guarda todo en un único archivo: database.db
# (se crea solo, no hace falta instalar ningún servidor de base de datos).
sqlite_url = "sqlite:///database.db"

# echo=True hace que SQLModel imprima por consola cada sentencia SQL que
# ejecuta. Es muy útil mientras estás aprendiendo, para ver qué es lo que
# realmente se manda a la base de datos.
engine = create_engine(sqlite_url, echo=False)


def create_db_and_tables() -> None:
    """Mira todos los modelos con table=True (Oficina, Persona) y crea
    sus tablas en la base de datos si todavía no existen."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Devuelve una sesión nueva para hacer operaciones sobre la base
    de datos (agregar, consultar, actualizar, borrar)."""
    return Session(engine)