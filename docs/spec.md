# RAG Hub: Spec Fase 1

## Objetivo
API monolítica modular para organizar documentos en colecciones. Es la base
sobre la que se montarán la ingesta (chunks y embeddings), el chat con RAG y
los evals en fases posteriores.

## Alcance
- CRUD de colecciones
- CRUD de documentos dentro de colecciones

## Fuera de alcance (por ahora)
- Autenticación y usuarios (siguiente entrega)
- Ingesta, embeddings, búsqueda semántica y chat
- Subida de archivos: el contenido llega como texto en el body

## Entidades

### Collection
| Campo       | Tipo          | Restricciones                 |
|-------------|---------------|-------------------------------|
| id          | UUID          | PK, generado por la app       |
| name        | string        | 1-100 chars, único, requerido |
| description | string / null | opcional                      |
| created_at  | timestamptz   | generado por la DB            |

### Document
| Campo         | Tipo        | Restricciones                                    |
|---------------|-------------|--------------------------------------------------|
| id            | UUID        | PK, generado por la app                          |
| collection_id | UUID        | FK a collections.id, ON DELETE CASCADE, indexado |
| title         | string      | 1-200 chars, requerido                           |
| content       | text        | requerido, no vacío                              |
| status        | string      | pending / processed / failed, default pending    |
| created_at    | timestamptz | generado por la DB                               |

## Reglas de negocio
1. El nombre de una colección es único. Duplicarlo devuelve 409.
2. Borrar una colección borra sus documentos (cascada en la DB).
3. No se puede crear un documento en una colección inexistente (404).
4. `status` no lo controla el cliente: nace en `pending` y solo lo cambiará
   el módulo de ingesta en la Fase 2.
5. PATCH es parcial: solo se modifican los campos enviados.

## Endpoints
| Método | Ruta                                | Descripción                  | Códigos            |
|--------|-------------------------------------|------------------------------|--------------------|
| POST   | /collections                        | Crear colección              | 201, 409, 422      |
| GET    | /collections                        | Listar (limit, offset)       | 200                |
| GET    | /collections/{id}                   | Obtener colección            | 200, 404           |
| PATCH  | /collections/{id}                   | Actualizar colección         | 200, 404, 409, 422 |
| DELETE | /collections/{id}                   | Borrar colección y docs      | 204, 404           |
| POST   | /collections/{collection_id}/documents | Crear documento           | 201, 404, 422      |
| GET    | /collections/{collection_id}/documents | Listar documentos (limit, offset) | 200, 404  |
| GET    | /documents/{id}                     | Obtener documento            | 200, 404           |
| PATCH  | /documents/{id}                     | Actualizar title/content     | 200, 404, 422      |
| DELETE | /documents/{id}                     | Borrar documento             | 204, 404           |

## Formato de errores
Por ahora el default de FastAPI: `{"detail": "mensaje"}`. Los 422 de
validación traen el detalle por campo. Se unificará más adelante.

## Contrato OpenAPI
Lo genera FastAPI (`/docs`, `/openapi.json`). Al cerrar la fase se exporta a
`docs/openapi.json`.

## Criterios de aceptación
- [ ] Todos los endpoints responden con los códigos de la tabla
- [ ] Borrar una colección elimina sus documentos
- [ ] Nombre de colección duplicado devuelve 409
- [ ] PATCH sin body útil no rompe ni borra campos
- [ ] Migraciones con Alembic aplican limpio sobre una DB vacía
- [ ] Tests de pytest para el camino feliz y los errores principales