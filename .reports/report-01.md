# Informe de estado del proyecto: rmu-api-attack

Fecha: 2026-05-12  
Repositorio: `/home/labcabrera/repositories/github/rmu/rmu-api-attack`

## Resumen ejecutivo

El proyecto implementa una API FastAPI para gestionar ataques de RMU con una separacion razonable por capas: dominio, casos de uso, puertos, infraestructura y controladores HTTP. La direccion arquitectonica es buena para una API backend mantenible, especialmente porque ya existe una distincion clara entre entidades de dominio, use cases, adaptadores de persistencia MongoDB y DTOs HTTP.

El estado actual, sin embargo, no puede considerarse estable desde el punto de vista de calidad de entrega: la suite de tests no pasa la fase de coleccion, el entorno local mezcla Poetry, `requirements.txt` y un `.venv` incompleto, y hay inconsistencias entre documentacion, configuracion y codigo. La recomendacion principal es ordenar primero la base de build y validacion, migrando a `uv` como gestor unico, y despues corregir tests y contratos API.

## Alcance revisado

Se revisaron los siguientes elementos:

- `pyproject.toml`, `poetry.lock`, `requirements.txt` y `.venv` existente.
- `Dockerfile`, `local-start.sh`, `local-test.sh` y documentacion principal.
- Estructura de paquetes bajo `app/` y `tests/`.
- Configuracion de FastAPI, contenedor de dependencias, repositorio MongoDB, cliente HTTP externo y DTOs.
- Estado de validacion local con `pytest`, `black` e `isort`.

No se ha encontrado un `AGENTS.md` local dentro del repositorio ni un directorio `.specify/`, por lo que no aplica flujo Spec Kit local.

## Estado de implementacion

### Arquitectura

El proyecto tiene una arquitectura por capas bastante reconocible:

- `app/domain`: entidades, enums, excepciones y servicios de dominio.
- `app/application`: comandos, puertos y casos de uso.
- `app/infrastructure`: configuracion, logging, persistencia MongoDB, cliente REST externo y contenedor DI.
- `app/interfaces/http`: controladores FastAPI y DTOs.
- `tests`: tests unitarios y de API.

Este enfoque es positivo porque reduce el acoplamiento directo entre FastAPI, MongoDB y reglas de negocio. Tambien facilita una futura mejora hacia tests mas aislados y adaptadores reemplazables.

### Funcionalidad cubierta

La API expone endpoints para:

- Buscar ataques por RSQL.
- Consultar un ataque por identificador.
- Crear ataques.
- Actualizar modificadores, parada, tirada, criticos y pifias.
- Eliminar ataques.
- Aplicar resultados al modulo tactico.
- Consultar `/health`.

El dominio ya incluye calculo de modificadores, estados de ataque, conversiones DTO/dominio y adaptadores para consultar tablas externas de ataque, critico y pifia.

### Estado de calidad automatizada

La suite de tests no esta en verde. El comando ejecutado:

```bash
.venv/bin/pytest -q
```

Resultado observado:

- Python 3.11.2.
- Pytest 7.4.3.
- 16 tests recogidos antes de interrupcion.
- 3 errores durante coleccion.

Errores principales:

- `tests/test_attack_domain_conversions.py` importa `Critical`, pero no existe exportado en `app.domain.entities`.
- `tests/test_attack_table_rest_adapter.py` importa `app.infrastructure.adapters.external.attack_table_rest_adapter`, pero el codigo real esta en `app.infrastructure.api_client.attack_table_rest_adapter`.
- `tests/test_attacks.py` importa `AttackMode`, pero no existe en los enums actuales.

Ademas, los tests de API usan rutas `/api/v1/attacks`, mientras que la aplicacion monta el router con `API_PREFIX = "/v1"`, por lo que la ruta real es `/v1/attacks`.

### Formato y tooling

`pyproject.toml` declara `black` e `isort` como dependencias de desarrollo de Poetry, pero no estan disponibles en el `.venv` actual:

```bash
.venv/bin/black --check app tests
.venv/bin/isort --check-only app tests
```

Ambos comandos fallan porque los binarios no existen. Esto apunta a que el entorno local no fue creado desde Poetry con dependencias de desarrollo, o que `requirements.txt` se esta usando como fuente practica de instalacion.

## Hallazgos principales

### 1. Gestion de dependencias fragmentada

Actualmente conviven tres fuentes de verdad:

- `pyproject.toml` con configuracion Poetry.
- `poetry.lock`.
- `requirements.txt`.

El `README.adoc` y los scripts locales instalan desde `requirements.txt`, mientras que el `Dockerfile` instala con Poetry. Esto crea riesgo de divergencia entre desarrollo local, CI y contenedor.

Impacto:

- Entornos reproducibles debiles.
- Dev dependencies no instaladas de forma consistente.
- Dificultad para automatizar lint, test y build.
- Mayor friccion para mantener versiones actualizadas.

### 2. Tests desalineados con el codigo actual

Los tests parecen arrastrar una API o modelo anterior:

- Importan clases o rutas que ya no existen.
- Usan nombres de campos antiguos como `tacticalGameId`, `input` o `mode`.
- Esperan `/api/v1`, pero el prefijo actual es `/v1`.
- Mockean proveedores de un contenedor que no es el mismo que usan los controladores.

Impacto:

- No hay red de seguridad fiable.
- Cualquier refactor de dependencias o migracion de tooling queda sin validacion.
- El estado real de la API solo puede inferirse parcialmente.

### 3. Configuracion inconsistente

La documentacion menciona variables como `MONGO_URI` y `MONGO_DATABASE`, pero el codigo usa `RMU_MONGO_ATTACK_URI`. En `MongoAttackRepository` existe una referencia a `settings.MONGODB_DATABASE`, pero `Settings` no define ese atributo.

Impacto:

- Riesgo de fallo en modo legacy del repositorio.
- Onboarding mas confuso.
- Diferencias entre `.env.example`, README y runtime real.

### 4. Excepciones HTTP en infraestructura

`MongoAttackRepository` importa y lanza `fastapi.HTTPException`. En una arquitectura por capas, la infraestructura no deberia depender de FastAPI ni decidir codigos HTTP.

Impacto:

- Acoplamiento innecesario entre persistencia y transporte HTTP.
- Casos de uso mas dificiles de probar.
- Reutilizacion limitada fuera de FastAPI.

Recomendacion:

- Lanzar excepciones de dominio o aplicacion (`AttackNotFoundException`, `RepositoryError`, `InvalidAttackIdError`).
- Traducirlas a HTTP en controladores o exception handlers globales.

### 5. Manejo de errores demasiado generico

Hay multiples `except Exception` que devuelven `500` con el texto interno de la excepcion. Tambien hay casos como `find_by_rsql` que hacen `print` y retornan una lista vacia ante error.

Impacto:

- Se ocultan errores reales como resultados vacios.
- Posible exposicion de detalles internos en respuestas HTTP.
- Observabilidad insuficiente para diagnostico.

### 6. Estandares de codigo incompletos

Hay señales de estilo inconsistente:

- `pyproject.toml` exige Python `^3.11`, pero Black configura `target-version = ['py38']`.
- Uso mixto de `camelCase` en variables internas de dominio (`sizeDif`, `basePenalty`, `calledShot`).
- Condiciones con formato no Black, por ejemplo `if(self.is_melee())`.
- Dependencias de desarrollo declaradas pero no disponibles en el entorno actual.
- No hay configuracion visible de type checking ni linter moderno.

### 7. Docker aun depende de Poetry

El `Dockerfile` instala Poetry 1.6.1 y usa `poetry install`. Si el proyecto migra a uv, el contenedor deberia cambiar tambien para evitar mantener dos flujos.

Impacto:

- Build mas lento de lo necesario.
- Mayor superficie de mantenimiento.
- Divergencia entre entorno local moderno y entorno de despliegue.

## Recomendacion principal: migrar de Poetry a uv

La migracion a `uv` es recomendable para este proyecto porque permitiria unificar instalacion, bloqueo, ejecucion de comandos y build con una herramienta mas rapida y simple. Tambien encaja mejor con un `pyproject.toml` moderno basado en PEP 621.

### Objetivo de la migracion

Dejar una unica fuente de verdad:

- `pyproject.toml` con `[project]`, dependencias y grupos de desarrollo.
- `uv.lock` como lockfile reproducible.
- Scripts/documentacion/Docker usando `uv`.
- Eliminar `poetry.lock` cuando la migracion este validada.
- Eliminar o regenerar `requirements.txt` solo si una plataforma externa lo exige.

### Propuesta de `pyproject.toml`

Estructura objetivo orientativa:

```toml
[project]
name = "rmu-api-attack"
version = "0.3.3"
description = "RMU API Attack - FastAPI application for managing RPG attacks"
readme = "README.adoc"
requires-python = ">=3.11,<3.13"
authors = [
  { name = "Lab Cabrera", email = "labcabrera@example.com" }
]
dependencies = [
  "fastapi>=0.104",
  "uvicorn[standard]>=0.24",
  "motor>=3.3",
  "pydantic>=2.4",
  "pymongo>=4.5",
  "httpx>=0.25",
  "dependency-injector>=4.41",
]

[dependency-groups]
dev = [
  "pytest>=7.4",
  "pytest-asyncio>=0.21",
  "ruff>=0.4",
  "mypy>=1.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]
```

Notas:

- `ruff` puede reemplazar a `black` e `isort` para formato e imports con menos herramientas.
- Si se prefiere mantener Black, tambien es valido, pero conviene evitar duplicidad innecesaria.
- La version de Python deberia alinearse con el runtime real. Si solo se soporta 3.11, usar `>=3.11,<3.12`; si se quiere abrir 3.12, validarlo en CI.

### Comandos objetivo con uv

```bash
uv sync --all-groups
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy app
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker objetivo

El `Dockerfile` deberia instalar dependencias con uv, por ejemplo:

```dockerfile
FROM python:3.11-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.11-slim AS production

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /app /app

RUN groupadd -r appuser && useradd -r -g appuser appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Conviene fijar una version concreta de la imagen o binario de uv en vez de `latest` cuando se estabilice el pipeline.

## Plan recomendado de mejora

### Prioridad 1: recuperar la base de validacion

1. Corregir imports y fixtures de tests para que reflejen el modelo actual.
2. Alinear rutas de tests con `/v1/attacks` o cambiar `API_PREFIX` si se quiere mantener `/api/v1`.
3. Evitar que los tests creen contenedores distintos al usado por el router.
4. Ejecutar `pytest` hasta que la suite este en verde.

### Prioridad 2: migrar tooling a uv

1. Convertir `pyproject.toml` de Poetry a PEP 621.
2. Crear `uv.lock` con `uv lock`.
3. Validar entorno con `uv sync --all-groups`.
4. Actualizar `README.adoc`, `local-start.sh`, `local-test.sh` y `Dockerfile`.
5. Retirar `poetry.lock` y decidir si `requirements.txt` se elimina o se genera desde uv para compatibilidad externa.

### Prioridad 3: estandarizar calidad de codigo

1. Adoptar `ruff` para formato, lint e imports.
2. Configurar `mypy` o `pyright` para al menos `app/application` y `app/domain`.
3. Ajustar `pytest-asyncio` explicitamente en `pyproject.toml`.
4. Anadir CI con pasos: `uv sync --all-groups`, `ruff format --check`, `ruff check`, `mypy`, `pytest`.

### Prioridad 4: endurecer arquitectura y errores

1. Sacar `HTTPException` de infraestructura.
2. Crear exception handlers globales en FastAPI.
3. Revisar `find_by_id`, `find_by_rsql`, `delete` y `exists` para no ocultar errores de ObjectId, MongoDB o RSQL.
4. No devolver detalles internos de excepciones en respuestas 500.

### Prioridad 5: configuracion y runtime

1. Unificar nombres de variables entre README, `.env.example` y codigo.
2. Definir `MONGODB_DATABASE` o eliminar referencias legacy.
3. Considerar `pydantic-settings` para configuracion tipada.
4. Cerrar clientes externos y conexiones en el lifespan de FastAPI.

## Mejoras concretas sugeridas

### Dependencias y estandares

- Sustituir Poetry por uv como flujo principal.
- Eliminar duplicidad `poetry.lock`/`requirements.txt`.
- Anadir `ruff` y `mypy`.
- Alinear version objetivo de Black/Ruff con Python 3.11.
- Separar dependencias runtime y dev mediante dependency groups.

### Testing

- Actualizar tests obsoletos antes de aumentar cobertura.
- Priorizar tests de dominio puro para calculos de ataque, criticos y pifias.
- Anadir tests de repositorio con fake/mocks de Motor o testcontainers si el proyecto ya acepta dependencias de integracion.
- Anadir tests de controladores con dependency overrides claros.
- Cubrir errores de ObjectId invalido, ataque inexistente, RSQL invalido y fallo del API externo de tablas.

### API y contratos

- Decidir prefijo definitivo: `/v1` o `/api/v1`.
- Usar DTOs especificos en `apply_attack_results` en lugar de `dict`.
- Normalizar codigos HTTP para no encontrado, validacion y conflictos de estado.
- Alinear README con la API real.

### Seguridad y observabilidad

- Evitar devolver mensajes internos de excepciones en HTTP 500.
- Sanitizar logs con datos sensibles de forma centralizada.
- No registrar objetos de request completos si pueden contener datos sensibles.
- Revisar el health check para no exponer URL de MongoDB mas alla de lo necesario.
- Incorporar correlation IDs si el ecosistema RMU ya los usa.

### Mantenibilidad de dominio

- Corregir nombres internos a `snake_case`.
- Revisar TODOs de calculo en tiradas criticas y pifias.
- Separar reglas de estado de ataque en un validador de transiciones.
- Evitar mutacion accidental acumulativa en `append_all_modifiers` si se llama mas de una vez sobre la misma entidad.

## Riesgos si se migra sin preparar

Migrar a uv sin arreglar primero los tests puede dejar el proyecto con un build mas moderno pero sin garantia funcional. El riesgo principal no es uv, sino no tener una suite fiable para confirmar que la migracion no cambia comportamiento.

Orden recomendado:

1. Congelar diagnostico actual.
2. Corregir tests minimos de coleccion.
3. Migrar pyproject y lockfile a uv.
4. Actualizar Docker/scripts/README.
5. Activar CI.

## Conclusion

El proyecto tiene una base funcional y una arquitectura con buena intencion de separacion por capas, pero necesita una estabilizacion de tooling y tests antes de considerarse mantenible. La migracion de Poetry a uv es una mejora adecuada y oportuna, siempre que se haga como parte de una limpieza integral de fuentes de verdad, validacion automatizada y estandares de codigo.

La prioridad recomendada es convertir `uv` en el flujo unico de desarrollo y CI, pero usar la migracion como catalizador para dejar la suite en verde, retirar dependencias duplicadas y establecer checks reproducibles.
