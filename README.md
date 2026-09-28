# Gestión de Oficinas y Personas — SQLModel

Práctica Profesionalizante I — Trabajo Práctico 3 (SQLModel)

Aplicación de ejemplo que modela una relación uno a muchos entre
Oficina y Persona usando SQLModel, implementando el ciclo CRUD
completo sobre ambos modelos.

## Instalación

1. Cloná el repositorio y ubicate en la carpeta raíz.
2. Creá y activá un entorno virtual:
   - python -m venv venv
   - source venv/bin/activate
3. Instalá las dependencias: pip install -r requirements.txt

## Ejecución

python -m project.app

## Modelo de datos

- Oficina: id, nombre, direccion.
- Persona: id, nombre, edad, puesto, oficina_id (clave foránea).

La relación uno a muchos se implementa con Relationship() en ambos
modelos, permitiendo navegarla en ambos sentidos:

persona.oficina      # la Oficina a la que pertenece esa Persona
oficina.personas     # la lista de Personas de esa Oficina# trabajo-practico-numero-3
