# RAG Hub

API para organizar documentos en colecciones. Es la base de un sistema RAG: en fases posteriores se agregan la ingesta (chunks y embeddings), el chat y los evals.

Hoy está en la **fase 1**: CRUD de colecciones y de documentos. El contenido llega como texto en el body. No hay autenticación, subida de archivos, embeddings ni búsqueda semántica.

El contrato de esta fase (entidades, reglas y endpoints) está en [`docs/spec.md`](docs/spec.md).

## Stack

| | |
|---|---|
| Lenguaje | Python 3.14 |
| API | FastAPI, servida con Uvicorn |
| Modelos y config | Pydantic, pydantic-settings |
| Acceso a datos | SQLAlchemy 2 (asyncio) y asyncpg |
| Migraciones | Alembic |
| Base de datos | PostgreSQL 17, imagen `pgvector/pgvector` (la extensión vector queda lista para la fase 2; esta fase no la usa) |
| Entorno | uv y Docker Compose |
| Desarrollo | pytest, Ruff, mypy, httpx |

## Cómo levantarlo

Hace falta Docker y [uv](https://docs.astral.sh/uv/).

```bash
docker compose up -d
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000`. La documentación interactiva está en `/docs`.

Postgres escucha en `localhost:5432`, base `raghub`, usuario y contraseña `postgres`. Esa URL ya es el valor por defecto (`postgresql+asyncpg://postgres:postgres@localhost:5432/raghub`). Para cambiarla, crea un `.env` en la raíz:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/raghub
```

Ese archivo no se sube al repositorio.

## Qué hay ahora

- `POST/GET/PATCH/DELETE /collections`
- `POST/GET /collections/{collection_id}/documents`
- `GET/PATCH/DELETE /documents/{id}`

Al cerrar la fase, el OpenAPI exportado queda en [`docs/openapi.json`](docs/openapi.json). FastAPI también lo sirve en `/openapi.json`.

## Tests

Los tests ejercitan la API contra una base aparte, `raghub_test`, en el mismo Postgres de Docker. No tocan la base `raghub`. Cubren el camino feliz y los errores del spec: 409 por nombre duplicado, 404, 422, cascada al borrar una colección y PATCH parcial.

Postgres tiene que estar levantado. La primera corrida crea `raghub_test` y aplica las migraciones.

```bash
docker compose up -d
uv run pytest
```
