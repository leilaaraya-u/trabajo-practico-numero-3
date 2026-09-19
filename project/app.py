from sqlmodel import Session, select

from .database import create_db_and_tables, get_session
from .models import Oficina, Persona


def create_oficinas(session: Session) -> None:
    oficina_central = Oficina(nombre="Casa Central", direccion="Av. Colón 123")
    oficina_sucursal = Oficina(nombre="Sucursal Norte", direccion="Bv. San Juan 456")

    # session.add() marca el objeto para ser guardado (todavía no toca
    # la base de datos). session.commit() sí lo escribe de verdad.
    session.add(oficina_central)
    session.add(oficina_sucursal)
    session.commit()

    # Después del commit, el objeto en Python queda "desactualizado"
    # (por ejemplo, no tiene el id que le asignó la base). refresh()
    # lo vuelve a leer para traer esos datos.
    session.refresh(oficina_central)
    session.refresh(oficina_sucursal)

    print("Oficinas creadas:", oficina_central, oficina_sucursal)


def create_personas(session: Session) -> None:
    # Primero busco las oficinas que ya existen en la base.
    oficina_central = session.exec(
        select(Oficina).where(Oficina.nombre == "Casa Central")
    ).first()
    oficina_sucursal = session.exec(
        select(Oficina).where(Oficina.nombre == "Sucursal Norte")
    ).first()

    # ACÁ está el punto clave del TP: le paso el objeto Oficina directo
    # al parámetro "oficina" (el relationship attribute). NO estoy
    # escribiendo oficina_id=1 a mano. SQLModel se encarga de completar
    # oficina_id solo, en base al objeto que le pasé.
    ana = Persona(nombre="Ana Gómez", edad=29, puesto="Recepcionista", oficina=oficina_central)
    luis = Persona(nombre="Luis Romano", edad=41, puesto="Contador", oficina=oficina_central)
    priscila = Persona(nombre="Priscila Pinto", edad=35, puesto="Vendedora", oficina=oficina_sucursal)

    session.add(ana)
    session.add(luis)
    session.add(priscila)
    session.commit()

    print("Personas creadas: Ana, Luis y Priscila")


def listar_personas_de_oficina(session: Session, nombre_oficina: str) -> None:
    """Lee las personas de una oficina navegando el relationship
    attribute oficina.personas — SQLModel arma el SELECT internamente,
    no hace falta escribir el JOIN a mano para esto."""
    oficina = session.exec(
        select(Oficina).where(Oficina.nombre == nombre_oficina)
    ).first()

    print(f"\nPersonas en {oficina.nombre}:")
    for persona in oficina.personas:
        print(f"  - {persona.nombre} ({persona.puesto})")


def listar_personas_con_join(session: Session) -> None:
    """Acá el JOIN sí se escribe explícitamente: unimos Persona con
    Oficina por la clave foránea, para traer datos de las dos tablas
    en una sola consulta."""
    statement = (
        select(Persona.nombre, Persona.puesto, Oficina.nombre)
        .join(Oficina, Persona.oficina_id == Oficina.id)
    )
    resultados = session.exec(statement).all()

    print("\nPersonas con su oficina (JOIN):")
    for nombre_persona, puesto, nombre_oficina in resultados:
        print(f"  - {nombre_persona} ({puesto}) trabaja en {nombre_oficina}")


def buscar_personas_por_puesto(session: Session, puesto: str) -> None:
    """Un filtro (WHERE) simple sobre un campo de Persona."""
    statement = select(Persona).where(Persona.puesto == puesto)
    personas = session.exec(statement).all()

    print(f"\nPersonas con puesto '{puesto}':")
    for persona in personas:
        print(f"  - {persona.nombre}")


def mover_persona_de_oficina(session: Session, nombre_persona: str, nombre_nueva_oficina: str) -> None:
    persona = session.exec(
        select(Persona).where(Persona.nombre == nombre_persona)
    ).first()
    nueva_oficina = session.exec(
        select(Oficina).where(Oficina.nombre == nombre_nueva_oficina)
    ).first()

    # De nuevo: reasigno el relationship attribute directamente
    # (persona.oficina = ...), no toco persona.oficina_id a mano.
    persona.oficina = nueva_oficina
    session.add(persona)
    session.commit()

    print(f"\n{persona.nombre} ahora trabaja en {persona.oficina.nombre}")


def eliminar_persona(session: Session, nombre_persona: str) -> None:
    persona = session.exec(
        select(Persona).where(Persona.nombre == nombre_persona)
    ).first()
    session.delete(persona)
    session.commit()
    print(f"\nSe eliminó a {nombre_persona}")


def eliminar_oficina(session: Session, nombre_oficina: str) -> None:
    """Si la oficina todavía tiene personas asociadas (oficina.personas
    no está vacío), NO la borramos: SQLModel/SQLAlchemy no reasigna ni
    borra en cascada por su cuenta. Si uno intentara borrarla igual sin
    este chequeo, la base de datos puede rechazar el DELETE por violar
    la clave foránea, o dejar personas con un oficina_id que ya no
    existe. Por eso frenamos acá y avisamos."""
    oficina = session.exec(
        select(Oficina).where(Oficina.nombre == nombre_oficina)
    ).first()

    if oficina.personas:
        print(
            f"\nNo se puede eliminar '{oficina.nombre}': todavía tiene "
            f"{len(oficina.personas)} persona(s) asociada(s)."
        )
        return

    session.delete(oficina)
    session.commit()
    print(f"\nSe eliminó la oficina '{nombre_oficina}'")


def main() -> None:
    # 1. Crear la base de datos y las tablas (si no existen).
    create_db_and_tables()

    # 2. Abro UNA sesión y la uso para todo el programa.
    with get_session() as session:
        create_oficinas(session)
        create_personas(session)

        listar_personas_de_oficina(session, "Casa Central")
        listar_personas_con_join(session)
        buscar_personas_por_puesto(session, "Contador")

        mover_persona_de_oficina(session, "Ana Gómez", "Sucursal Norte")
        listar_personas_de_oficina(session, "Sucursal Norte")

        eliminar_persona(session, "Luis Romano")

        # Esto va a imprimir el aviso de "no se puede eliminar", porque
        # Sucursal Norte todavía tiene personas (Ana y Priscila).
        eliminar_oficina(session, "Sucursal Norte")


# Este if hace que main() se ejecute SOLO cuando corrés este archivo
# directamente (python -m project.app), y no si alguien importa app.py
# desde otro lado.
if __name__ == "__main__":
    main()