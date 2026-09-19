from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


# "table=True" le dice a SQLModel: esta clase NO es solo para validar datos,
# es una tabla de verdad en la base de datos.
class Oficina(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    direccion: str

    # Esto NO es una columna. Es un "relationship attribute": le dice a
    # SQLModel "cuando alguien pida oficina.personas, andá a buscar todas
    # las filas de la tabla Persona cuyo oficina_id sea el mío".
    # back_populates="oficina" lo conecta con el atributo "oficina" de
    # la clase Persona, de abajo, para que la relación funcione en los
    # dos sentidos con un solo par de atributos.
    personas: List["Persona"] = Relationship(back_populates="oficina")


class Persona(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    edad: Optional[int] = None
    puesto: Optional[str] = None

    # ESTA sí es una columna real: la clave foránea. Guarda el id de la
    # oficina a la que pertenece la persona. Es la que efectivamente
    # existe en la tabla "persona" de la base de datos.
    oficina_id: Optional[int] = Field(default=None, foreign_key="oficina.id")

    # Y este es el relationship attribute del lado "Persona": permite
    # escribir persona.oficina para obtener el objeto Oficina completo,
    # en vez de tener que buscarlo a mano por oficina_id.
    oficina: Optional[Oficina] = Relationship(back_populates="personas")