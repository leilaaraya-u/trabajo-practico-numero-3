from sqlmodel import select

from .database import create_db_and_tables, get_session
from .models import Oficina, Persona


def create_oficinas() -> None:
    """
    Alta de oficinas de ejemplo.

    Idempotente: si ya existe una oficina con ese nombre, no la vuelve a
    crear. Esto permite ejecutar el script varias veces sobre el mismo
    database.db sin generar datos duplicados.
    """
    datos = [
        ("Oficina Centro", "Av. Colón 123"),
        ("Oficina Norte", "Av. Rafael Núñez 4500"),
    ]

    with get_session() as session:
        for nombre, direccion in datos:
            existente = session.exec(
                select(Oficina).where(Oficina.nombre == nombre)
            ).first()
            if existente:
                print(f"Ya existía: {existente}")
                continue

            oficina = Oficina(nombre=nombre, direccion=direccion)
            session.add(oficina)
            session.commit()
            print(f"Creada: {oficina}")


def create_personas() -> None:
    """
    Alta de personas asociadas a oficinas mediante el atributo de relación.

    Importante: no se asigna oficina_id a mano; se asigna el objeto Oficina
    directamente al atributo 'oficina' (relationship attribute), o se agrega
    la persona a oficina.personas.

    Si ya existe una persona con ese nombre, no la vuelve a
    crear, para poder correr el script varias veces sin duplicar datos.
    """
    with get_session() as session:
        oficina_centro = session.exec(
            select(Oficina).where(Oficina.nombre == "Oficina Centro")
        ).first()

        if not oficina_centro:
            print("No existe 'Oficina Centro'. Ejecutá create_oficinas() primero.")
            return

        ya_existe_ana = session.exec(
            select(Persona).where(Persona.nombre == "Ana Gómez")
        ).first()
        ya_existe_luis = session.exec(
            select(Persona).where(Persona.nombre == "Luis Pérez")
        ).first()

        if ya_existe_ana and ya_existe_luis:
            print("Las personas de ejemplo ya existían, no se crean de nuevo.")
            return

        if not ya_existe_ana:
            persona1 = Persona(nombre="Ana Gómez", edad=29, puesto="Desarrolladora")
            # Asociación vía relationship attribute, no vía id foráneo manual.
            persona1.oficina = oficina_centro
            session.add(persona1)
            print(f"Creada: {persona1}")

        if not ya_existe_luis:
            persona2 = Persona(nombre="Luis Pérez", edad=35, puesto="Analista")
            oficina_centro.personas.append(persona2)
            session.add(persona2)
            print(f"Creada: {persona2}")

        session.commit()



def listar_personas_de_oficina(nombre_oficina: str) -> None:
    """Lista todas las personas de una oficina navegando oficina.personas."""
    with get_session() as session:
        oficina = session.exec(
            select(Oficina).where(Oficina.nombre == nombre_oficina)
        ).first()

        if not oficina:
            print(f"No se encontró la oficina '{nombre_oficina}'.")
            return

        print(f"Personas en {oficina.nombre}:")
        for persona in oficina.personas:
            print(f"  - {persona.nombre} ({persona.puesto})")


def personas_con_join() -> None:
    """Consulta con JOIN explícito entre Persona y Oficina."""
    with get_session() as session:
        statement = (
            select(Persona, Oficina)
            .join(Oficina, Persona.oficina_id == Oficina.id)
        )
        resultados = session.exec(statement).all()

        print("Personas con su oficina (JOIN):")
        for persona, oficina in resultados:
            print(f"  - {persona.nombre} trabaja en {oficina.nombre}")


def buscar_personas_por_nombre(fragmento: str) -> None:
    """Filtro (WHERE) sobre el campo nombre, usando LIKE."""
    with get_session() as session:
        statement = select(Persona).where(Persona.nombre.contains(fragmento))
        resultados = session.exec(statement).all()

        print(f"Personas cuyo nombre contiene '{fragmento}':")
        for persona in resultados:
            print(f"  - {persona.nombre}")


def buscar_personas_por_edad_minima(edad_minima: int) -> None:
    """Otro filtro (WHERE) de ejemplo, sobre un campo numérico."""
    with get_session() as session:
        statement = select(Persona).where(Persona.edad >= edad_minima)
        resultados = session.exec(statement).all()

        print(f"Personas con edad >= {edad_minima}:")
        for persona in resultados:
            print(f"  - {persona.nombre} ({persona.edad} años)")



def reasignar_persona_a_oficina(nombre_persona: str, nombre_nueva_oficina: str) -> None:
    """Reasigna una persona de su oficina actual a otra, vía relationship attribute."""
    with get_session() as session:
        persona = session.exec(
            select(Persona).where(Persona.nombre == nombre_persona)
        ).first()
        nueva_oficina = session.exec(
            select(Oficina).where(Oficina.nombre == nombre_nueva_oficina)
        ).first()

        if not persona or not nueva_oficina:
            print("No se encontró la persona o la oficina indicada.")
            return

        persona.oficina = nueva_oficina
        session.add(persona)
        session.commit()
        session.refresh(persona)
        print(f"{persona.nombre} fue reasignada a {persona.oficina.nombre}")


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def eliminar_persona(nombre_persona: str) -> None:
    """Elimina una persona de la base de datos."""
    with get_session() as session:
        persona = session.exec(
            select(Persona).where(Persona.nombre == nombre_persona)
        ).first()

        if not persona:
            print(f"No se encontró la persona '{nombre_persona}'.")
            return

        session.delete(persona)
        session.commit()
        print(f"Persona '{nombre_persona}' eliminada.")


def eliminar_oficina(nombre_oficina: str) -> None:
    """
    Intenta eliminar una oficina.

    Nota (ver informe): con la configuración por defecto de SQLModel/SQLAlchemy,
    si la oficina todavía tiene personas asociadas, la columna oficina_id de
    esas personas queda en NULL (no se produce un error), porque no se definió
    un ondelete="CASCADE" ni una validación manual previa. Para evitar
    inconsistencias, se recomienda chequear antes si oficina.personas está
    vacía, o definir explícitamente el comportamiento deseado (restringir,
    poner en null, o eliminar en cascada) en la relación.
    """
    with get_session() as session:
        oficina = session.exec(
            select(Oficina).where(Oficina.nombre == nombre_oficina)
        ).first()

        if not oficina:
            print(f"No se encontró la oficina '{nombre_oficina}'.")
            return

        if oficina.personas:
            print(
                f"La oficina '{nombre_oficina}' tiene {len(oficina.personas)} "
                "persona(s) asociada(s). Reasignalas o eliminalas antes de "
                "borrar la oficina."
            )
            return

        session.delete(oficina)
        session.commit()
        print(f"Oficina '{nombre_oficina}' eliminada.")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    create_db_and_tables()

    create_oficinas()
    create_personas()

    listar_personas_de_oficina("Oficina Centro")
    personas_con_join()
    buscar_personas_por_nombre("Ana")
    buscar_personas_por_edad_minima(30)

    reasignar_persona_a_oficina("Ana Gómez", "Oficina Norte")
    listar_personas_de_oficina("Oficina Norte")

    eliminar_persona("Luis Pérez")
    eliminar_oficina("Oficina Norte")   # tiene a Ana -> el chequeo lo impide
    eliminar_oficina("Oficina Centro")  # oficina vacía -> se elimina sin problema



# Este if hace que main() se ejecute SOLO cuando corrés este archivo
# directamente (python -m project.app), y no si alguien importa app.py
# desde otro lado.
if __name__ == "__main__":
    main()