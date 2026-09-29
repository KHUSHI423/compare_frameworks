# Taskboard Framework Benchmark

A comparative benchmark of three popular Python backend frameworks — **Django REST Framework, FastAPI, and Flask** — using the same Taskboard REST API.

The project implements equivalent functionality across all three frameworks and evaluates them across:

* API feature parity
* Performance and concurrency
* Codebase size and boilerplate
* Developer productivity
* Validation and authentication
* Database interaction
* File upload and CSV export behavior
* Pagination
* Error handling
* Architectural trade-offs

The goal is to make the comparison as fair as possible by exposing the **same API capabilities and behavior** through three independent implementations.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Architecture](#architecture)
* [Framework Implementations](#framework-implementations)
* [API Endpoints](#api-endpoints)
* [Project Structure](#project-structure)
* [Running the Project](#running-the-project)
* [API Parity Testing](#api-parity-testing)
* [Load Testing with Locust](#load-testing-with-locust)
* [Benchmark Methodology](#benchmark-methodology)
* [Challenges and Resolved Issues](#challenges-and-resolved-issues)
* [Framework Comparison](#framework-comparison)
* [Codebase Footprint](#codebase-footprint)
* [Endpoint-Level Technical Trade-offs](#endpoint-level-technical-trade-offs)
* [Benchmark Findings](#benchmark-findings)
* [Conclusion](#conclusion)

---

# Project Overview

The **Taskboard Framework Benchmark** implements the same Taskboard REST API using three different Python backend frameworks:

1. **Django 5 + Django REST Framework**
2. **FastAPI**
3. **Flask**

Each implementation supports authentication, boards, tasks, file attachments, CSV export, pagination, filtering, and authorization.

A shared test suite verifies that the implementations provide equivalent route coverage and response behavior.

A shared Locust scenario is used to benchmark the implementations under load.

The project also maintains a canonical **OpenAPI 3.0 specification** describing the API contract.

---

# Architecture

The repository is divided into three independent backend implementations and a shared benchmarking layer.

```text
                         Taskboard REST API
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
        Django REST          FastAPI             Flask
             │                  │                  │
             ▼                  ▼                  ▼
          Django ORM       SQLAlchemy Async   Flask-SQLAlchemy
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                         Same API Contract
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
             ▼                                     ▼
       API Parity Tests                      Locust Benchmarks
```

The repository contains:

```text
taskboard-benchmark/
│
├── django_app/
│   └── Django + Django REST Framework
│
├── fastapi_app/
│   └── FastAPI + SQLAlchemy + Pydantic
│
├── flask_app/
│   └── Flask + Flask-SQLAlchemy + Marshmallow
│
└── shared/
    ├── tests/
    │   └── test_api_parity.py
    │
    ├── benchmarks/
    │   └── locustfile.py
    │
    └── schemas/
        └── openapi_spec.json
```

---

# Framework Implementations

## 1. Django

Located in:

```text
django_app/
```

Technology stack:

* Django 5
* Django REST Framework
* SimpleJWT
* Django ORM
* DRF Serializers
* DRF ViewSets
* DRF Pagination

Django provides a large amount of functionality out of the box, allowing the implementation to remain relatively compact.

Authentication uses Django's built-in password hashing infrastructure together with `rest_framework_simplejwt`.

---

## 2. FastAPI

Located in:

```text
fastapi_app/
```

Technology stack:

* FastAPI
* Uvicorn
* SQLAlchemy Async
* Pydantic v2
* Passlib
* PyJWT
* OAuth2PasswordBearer
* Async SQLite / `aiosqlite`

FastAPI uses an asynchronous ASGI architecture and explicit dependency injection for database sessions.

It also automatically generates OpenAPI documentation and Swagger UI.

API documentation is available through:

```text
/docs
```

---

## 3. Flask

Located in:

```text
flask_app/
```

Technology stack:

* Flask
* Flask-SQLAlchemy
* Flask-Marshmallow
* PyJWT
* SQLAlchemy

Flask provides a lightweight core and leaves architectural decisions largely to the developer.

Authentication, validation, database integration, and request handling are explicitly implemented.

---

# API Endpoints

All three frameworks expose the same core API.

| Endpoint                             | Method   | Description                                           |
| ------------------------------------ | -------- | ----------------------------------------------------- |
| `/auth/signup`                       | `POST`   | Register a new user                                   |
| `/auth/login`                        | `POST`   | Authenticate and receive JWT access token             |
| `/auth/me`                           | `GET`    | Retrieve authenticated user profile                   |
| `/boards`                            | `GET`    | List owned boards with pagination                     |
| `/boards`                            | `POST`   | Create a new board                                    |
| `/boards/{board_id}`                 | `GET`    | Retrieve an owned board                               |
| `/boards/{board_id}`                 | `DELETE` | Delete an owned board                                 |
| `/boards/{board_id}/attachment`      | `POST`   | Upload a board attachment                             |
| `/boards/{board_id}/export`          | `GET`    | Export board tasks as CSV                             |
| `/boards/{board_id}/tasks`           | `GET`    | List board tasks with pagination and status filtering |
| `/boards/{board_id}/tasks`           | `POST`   | Create a task                                         |
| `/boards/{board_id}/tasks/{task_id}` | `PATCH`  | Update task details/status                            |
| `/boards/{board_id}/tasks/{task_id}` | `DELETE` | Delete a task                                         |

---

# Authentication Flow

The authentication flow is consistent across the implementations:

```text
                 POST /auth/signup
                        │
                        ▼
                  Create User
                        │
                        ▼
                 Password Hashing
                        │
                        ▼
                  User Database
```

Login:

```text
                 POST /auth/login
                        │
                        ▼
                Validate Credentials
                        │
                        ▼
                  Generate JWT
                        │
                        ▼
                Return Access Token
```

Authenticated requests use the JWT token:

```http
Authorization: Bearer <access_token>
```

The `/auth/me` endpoint uses the authenticated identity to retrieve the current user's profile.

---

# Project Structure

```text
taskboard-benchmark/
│
├── django_app/
│   ├── ...
│   └── tests/
│
├── fastapi_app/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── ...
│   └── tests/
│
├── flask_app/
│   ├── app/
│   │   ├── routes/
│   │   ├── models.py
│   │   └── ...
│   └── tests/
│
└── shared/
    ├── tests/
    │   └── test_api_parity.py
    │
    ├── benchmarks/
    │   └── locustfile.py
    │
    └── schemas/
        └── openapi_spec.json
```

---

# Running the Project

Each framework is implemented as a self-contained application.

Start the desired framework using its corresponding application configuration.

For FastAPI, the application exposes automatic API documentation at:

```text
/docs
```

The OpenAPI specification can also be generated using:

```bash
cd fastapi_app
python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > ../shared/schemas/openapi_spec.json
```

The generated specification provides a canonical machine-readable representation of the API contract.

---

# API Parity Testing

The project includes a shared automated parity test suite.

The objective is to verify that all three implementations provide equivalent:

* Routes
* HTTP methods
* Authentication behavior
* Validation behavior
* Status codes
* Response structures
* Authorization behavior
* Pagination behavior
* Task operations
* Board operations

Run the parity suite with:

```bash
python -m unittest shared/tests/test_api_parity.py
```

The tests are particularly important because framework defaults can produce different responses even when the underlying business logic is identical.

---

# Load Testing with Locust

The project uses **Locust** to benchmark the three implementations.

The shared scenario is located at:

```text
shared/benchmarks/locustfile.py
```

Run Locust against a running server:

```bash
locust -f shared/benchmarks/locustfile.py --host=http://localhost:8000
```

The benchmark scenario covers representative Taskboard workflows, including:

* Authentication
* Board operations
* Task operations
* Read-heavy workloads
* Write workloads
* Mixed API activity

This allows the frameworks to be compared under equivalent request patterns.

---

# Benchmark Methodology

The benchmark evaluates the implementations from multiple perspectives.

## Performance

Measured through:

* Requests per second
* Request latency
* Concurrent request handling
* Read/write workloads
* Database interaction
* File operations

## Code Complexity

Measured through:

* Approximate lines of code
* Amount of framework boilerplate
* Explicit versus generated CRUD logic
* Validation implementation
* Authentication implementation
* Dependency configuration

## Feature Parity

The same API behavior is implemented across:

* Authentication
* Authorization
* Boards
* Tasks
* Attachments
* CSV export
* Pagination
* Filtering
* Error handling

---

# Challenges and Resolved Issues

During implementation and parity testing, several framework-specific differences and bugs were identified.

## 1. HTTP Status Code and Response Parity

### Duplicate User Registration: `400` vs `409`

Django REST Framework's default `UniqueValidator` returned:

```http
400 Bad Request
```

for duplicate signup attempts.

FastAPI and Flask returned:

```http
409 Conflict
```

To maintain parity, Django's `SignupView` was updated to explicitly check whether the username or email already exists.

The standardized response became:

```json
{
  "error": "Username or email already exists"
}
```

with:

```http
409 Conflict
```

---

### Authorization: `404` vs `403`

Django's initial implementation filtered boards using:

```python
Board.objects.filter(owner=request.user)
```

As a result, attempting to access another user's board caused Django REST Framework to return:

```http
404 Not Found
```

The other implementations returned:

```http
403 Forbidden
```

The Django `BoardViewSet` was therefore changed so that detail endpoints retrieve the object first and explicitly verify ownership.

Unauthorized access now raises:

```python
PermissionDenied
```

resulting in:

```http
403 Forbidden
```

---

# 2. ORM and Query Warnings

## Django Unordered Pagination

Django produced:

```text
UnorderedObjectListWarning:
Pagination may yield inconsistent results with an unordered object_list
```

The solution was to define deterministic ordering in the model metadata:

```python
class Meta:
    ordering = ["id"]
```

This was applied to both:

* `Board`
* `Task`

---

## SQLAlchemy `Query.get()` Deprecation

Flask initially used:

```python
Board.query.get(board_id)
```

SQLAlchemy 2.0 considers this a legacy API.

It was replaced with:

```python
db.session.get(Board, board_id)
```

This removes the `LegacyAPIWarning` and uses the current SQLAlchemy API.

---

# 3. Validation and Input Handling

## Flask Empty Board Titles

The original Flask implementation only checked whether `title` existed:

```python
if "title" not in data:
```

This allowed:

```json
{
  "title": ""
}
```

to pass validation.

The validation was strengthened to ensure that the value is both a string and non-empty after trimming:

```python
isinstance(data.get("title"), str) and data["title"].strip()
```

---

# 4. Deprecations and Python Compatibility

## Pydantic V1 Configuration

The original FastAPI settings implementation used the deprecated Pydantic V1 style:

```python
class Config:
    ...
```

With Pydantic v2, this generated:

```text
PydanticDeprecatedSince20
```

The configuration was migrated to:

```python
model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore"
)
```

This aligns the settings implementation with Pydantic v2.

---

## `datetime.utcnow()` Deprecation

Python 3.12+ generated deprecation warnings for:

```python
datetime.utcnow()
```

The implementations were updated to use timezone-aware UTC timestamps:

```python
datetime.now(timezone.utc)
```

This avoids naive UTC datetime objects and removes the deprecation warnings.

---

# 5. Test Lifecycle and Database Isolation

## FastAPI Async Engine Initialization

FastAPI tests initially bypassed the Starlette lifespan context.

As a result, database initialization did not always execute:

```python
Base.metadata.create_all
```

This resulted in errors such as:

```text
OperationalError: no such table: users
```

The tests were updated to use the `TestClient` as a context manager:

```python
with TestClient(app) as client:
    ...
```

This ensures that application startup and database initialization hooks execute correctly.

---

## Database State Collisions

Running tests repeatedly against disk-backed SQLite databases caused old user records to remain.

This resulted in duplicate-user failures:

```http
409 Conflict
```

even though the test itself was not intended to test duplicate registration.

The test suites were updated to:

1. Use dynamically generated user identifiers.
2. Generate unique values using `uuid.uuid4()`.
3. Use clean in-memory databases where appropriate.

This makes individual test runs isolated and repeatable.

---

# 6. Missing Framework Assets

Several repository assets were initially empty:

```text
locustfile.py
openapi_spec.json
README.md
fastapi_app/tests/
flask_app/tests/
```

These were subsequently populated with:

* Comprehensive API parity tests
* Locust benchmark scenarios
* OpenAPI 3.0 specification
* Framework-specific test suites
* Project documentation

---

# Framework Comparison

The three frameworks take significantly different architectural approaches.

| Criteria            | Django REST Framework           | FastAPI                                | Flask                  |
| ------------------- | ------------------------------- | -------------------------------------- | ---------------------- |
| Execution Model     | Synchronous WSGI                | Asynchronous ASGI                      | Synchronous WSGI       |
| I/O Handling        | Blocking / Sync ORM             | Non-blocking / Async ORM               | Blocking / Sync ORM    |
| Validation          | DRF Serializers                 | Pydantic v2                            | Marshmallow / Manual   |
| API Documentation   | Manual / Third-party            | Automatic OpenAPI / Swagger            | Manual / Third-party   |
| Database Migrations | Built-in Django migrations      | External Alembic                       | External Flask-Migrate |
| Architecture        | Batteries-included              | Type-driven / async                    | Minimal / flexible     |
| Primary Strength    | Rapid full-featured development | Async APIs and automatic documentation | Lightweight control    |

---

# Developer Productivity and Ecosystem

## Django REST Framework

Django provides a large amount of functionality out of the box.

Important productivity features include:

* Built-in user models
* `AbstractUser`
* Django Admin
* Database migrations
* Django ORM
* DRF Serializers
* `ModelViewSet`
* `DefaultRouter`
* Pagination

The combination of these features significantly reduces the amount of application-specific CRUD code required.

---

## FastAPI

FastAPI focuses heavily on type hints and explicit API contracts.

Important features include:

* Automatic OpenAPI generation
* Swagger UI at `/docs`
* Pydantic v2 validation
* Python type hints
* Dependency injection
* Async request handling
* Automatic structured validation errors

FastAPI therefore provides a strong developer experience for API-focused applications.

---

## Flask

Flask intentionally provides a smaller core.

The developer chooses the surrounding components.

In this implementation, Flask requires explicit integration of:

* SQLAlchemy
* Marshmallow
* JWT authentication
* Validation
* Route handling
* Database operations

This gives developers significant architectural freedom but also increases the amount of application-level code.

---

# Codebase Footprint

The project-specific implementation produced approximately the following code footprints:

| Metric                |            Django |                      FastAPI |                 Flask |
| --------------------- | ----------------: | ---------------------------: | --------------------: |
| Approx. Lines of Code |              ~200 |                         ~450 |                  ~370 |
| Route Organization    | ViewSets + Router |                    APIRouter |             Blueprint |
| Validation            |   ModelSerializer |                  Pydantic v2 |  Marshmallow + Manual |
| Authentication        |         SimpleJWT | OAuth2PasswordBearer + PyJWT | JWT decorator + PyJWT |
| CRUD Abstraction      |              High |                     Explicit |              Explicit |

These numbers are specific to this repository and should not be interpreted as universal framework code-size measurements.

---

# Why the Code Sizes Differ

## Django

Django has the smallest implementation footprint in this project.

`ModelViewSet` and `DefaultRouter` automatically provide much of the CRUD functionality for:

```text
/boards
/boards/{board_id}
/boards/{board_id}/tasks
```

As a result, fewer explicit route handlers are required.

---

## FastAPI

FastAPI has the largest implementation footprint in this project.

This is primarily because the implementation explicitly defines:

* Pydantic schemas
* Async database sessions
* Dependency injection
* Authentication helpers
* Database operations
* API routes

The additional code provides greater explicitness and type-driven validation.

---

## Flask

Flask sits between the two implementations.

Its lightweight core requires explicit implementation of:

* Route handlers
* Validation
* JWT context
* Database operations
* Serialization

However, it avoids some of the additional structure required by the FastAPI implementation.

---

# Endpoint-Level Technical Trade-offs

## Authentication

### FastAPI and Flask

These implementations use:

```text
Passlib
   +
bcrypt
   +
PyJWT
```

Duplicate registration is explicitly checked using database queries and produces:

```http
409 Conflict
```

---

### Django

Django uses its built-in password hashing infrastructure.

JWT authentication is provided through:

```text
rest_framework_simplejwt
```

Custom signup handling was required to make duplicate registration behavior consistent with the other implementations.

---

# File Uploads

The endpoint is:

```text
POST /boards/{board_id}/attachment
```

### FastAPI

FastAPI uses:

```python
UploadFile
```

and asynchronous file reads:

```python
await file.read()
```

This allows file I/O to integrate with the asynchronous request model.

---

### Django

Django uses chunked file iteration:

```python
for chunk in file.chunks():
    ...
```

This avoids loading the entire file into memory at once.

---

### Flask

Flask uses:

```python
file.save(...)
```

The operation is synchronous and therefore blocks the worker handling that request until the write completes.

---

# CSV Export

The endpoint is:

```text
GET /boards/{board_id}/export
```

### Django

Django uses:

```python
Task.objects.filter(...).iterator()
```

to process database records in chunks rather than loading the entire result set into memory.

---

### FastAPI

FastAPI uses:

```python
StreamingResponse
```

together with:

```python
io.StringIO()
```

to stream the generated CSV response.

---

### Flask

Flask constructs the complete CSV in memory using:

```python
io.BytesIO(si.getvalue())
```

before returning it through:

```python
send_file
```

For large exports, this can result in higher memory consumption.

---

# Pagination

FastAPI and Flask implement a custom pagination response:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 10
}
```

Django REST Framework uses its native `PageNumberPagination` format:

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

Django also required deterministic model ordering to avoid inconsistent pagination warnings.

---

# Performance and Execution Model

## FastAPI

FastAPI uses:

```text
ASGI
  +
Uvicorn
  +
asyncio
  +
Async database sessions
```

The implementation is designed around non-blocking I/O and asynchronous request processing.

In the project's Locust benchmark, FastAPI achieved the highest throughput on the tested mixed read/write workload.

---

## Flask

Flask uses a WSGI architecture.

Its minimal request-processing layer can provide low overhead for simple operations.

The benchmark showed low single-request processing latency for the tested basic:

```text
GET /auth/me
```

operation.

For heavy concurrent I/O workloads, deployment can be scaled through multiple workers and appropriate worker configurations.

---

## Django REST Framework

Django uses a synchronous WSGI model and provides a larger framework stack.

The additional middleware, ORM abstraction, serializer processing, and framework functionality introduce additional request-processing overhead.

At the same time, Django provides strong built-in support for relational data handling, transactions, migrations, and cascading relationships.

---

# Empirical Benchmark Findings

The Locust benchmark produced the following project-specific observations.

## FastAPI

Observed strengths:

* Highest concurrency throughput in the tested mixed workload
* Strong performance for concurrent board/task operations
* Non-blocking asynchronous database sessions
* Async file handling
* Streaming responses
* Automatic API documentation

The project observed that asynchronous database sessions helped avoid thread starvation during concurrent request spikes.

---

## Flask

Observed strengths:

* Low latency for simple individual requests
* Minimal request-processing layer
* Lightweight architecture
* Fine-grained control over routes and database queries

The tested basic `/auth/me` request showed the lowest single-request processing latency among the three implementations.

---

## Django

Observed strengths:

* Strong built-in data-management capabilities
* Built-in migrations
* Relational ORM
* Transaction support
* Cascading relationships
* Reduced CRUD boilerplate

The project observed higher serializer and framework processing overhead compared with the lighter implementations.

---

# Key Architectural Takeaways

## FastAPI

The implementation demonstrates the advantages of an async-first API architecture.

```text
ASGI
 ↓
Async Request Handling
 ↓
Async Database Access
 ↓
Non-blocking I/O
 ↓
High Concurrency
```

It is particularly suitable when the API needs:

* High concurrent request handling
* Async I/O
* Automatic API documentation
* Strong request/response typing

---

## Django REST Framework

The implementation demonstrates the value of a batteries-included framework.

```text
Django
 ↓
ORM
 ↓
Authentication
 ↓
Migrations
 ↓
Admin
 ↓
DRF
 ↓
Serializers + ViewSets + Routers
```

This substantially reduces the amount of infrastructure that developers need to implement themselves.

---

## Flask

The Flask implementation demonstrates the benefits of a minimal framework.

```text
Flask Core
    │
    ├── SQLAlchemy
    ├── Marshmallow
    ├── PyJWT
    └── Custom Application Logic
```

This architecture gives developers more control over individual components and application structure.

---

# Project Conclusion

This benchmark demonstrates that framework selection involves trade-offs rather than a single universal choice.

### FastAPI

The Taskboard implementation demonstrates strong performance under the tested concurrent workload, automatic API documentation, type-driven validation, and asynchronous I/O.

### Django REST Framework

The implementation demonstrates high developer productivity through built-in authentication support, migrations, ORM functionality, serializers, routers, and CRUD abstractions.

### Flask

The implementation demonstrates the advantages of a lightweight framework with minimal assumptions and granular control over application architecture.

The appropriate choice depends on the application's requirements:

| Requirement                     | Relevant Implementation Strength |
| ------------------------------- | -------------------------------- |
| High concurrent API workload    | FastAPI                          |
| Automatic OpenAPI / Swagger     | FastAPI                          |
| Async I/O                       | FastAPI                          |
| Rapid CRUD development          | Django                           |
| Built-in migrations             | Django                           |
| Built-in admin ecosystem        | Django                           |
| Minimal framework overhead      | Flask                            |
| Maximum architectural freedom   | Flask                            |
| Explicit route/database control | Flask                            |

The benchmark should therefore be interpreted as a **project-specific comparison**, not a universal ranking of the three frameworks.

---

# What This Project Demonstrates

Beyond comparing frameworks, this project demonstrates practical backend engineering skills:

* REST API design
* Authentication and JWT
* Authorization
* Database modeling
* ORM usage
* Async database access
* Input validation
* API schema design
* OpenAPI
* Pagination
* File uploads
* Streaming responses
* CSV generation
* Automated API testing
* Cross-framework parity testing
* Load testing with Locust
* Debugging framework-specific behavior
* Handling deprecations
* Database isolation
* Performance analysis
* Architectural trade-off analysis

---

# Technologies

| Category       | Technologies                                  |
| -------------- | --------------------------------------------- |
| Backend        | Django, Django REST Framework, FastAPI, Flask |
| API            | REST, OpenAPI 3.0                             |
| Authentication | JWT, SimpleJWT, PyJWT                         |
| Validation     | DRF Serializers, Pydantic v2, Marshmallow     |
| ORM            | Django ORM, SQLAlchemy                        |
| Async          | asyncio, Async SQLAlchemy, aiosqlite          |
| Server         | Uvicorn / WSGI servers                        |
| Database       | SQLite                                        |
| Testing        | Python `unittest`, framework test clients     |
| Load Testing   | Locust                                        |
| Documentation  | OpenAPI / Swagger                             |

---

# Final Summary

The **Taskboard Framework Benchmark** provides three functionally equivalent REST API implementations and uses shared tests and load-testing scenarios to expose the practical differences between Django REST Framework, FastAPI, and Flask.

The project focuses not only on raw performance, but also on:

> **API parity + correctness + maintainability + developer productivity + performance + architectural flexibility**

This makes the repository a practical reference for understanding how the same backend system changes when implemented using three different Python web frameworks.



# Framework Insights & Architectural Learnings

The benchmark provided several practical insights into how Django REST Framework, FastAPI, and Flask approach backend development. These observations are specific to the implementations and workloads in this repository.

## Django REST Framework — Abstraction and Productivity

The Django implementation had the smallest code footprint in this project at approximately **200 lines**. This was largely enabled by Django REST Framework's higher level of abstraction through features such as:

* `ModelViewSet`
* `DefaultRouter`
* Model serializers
* Django ORM
* Built-in authentication infrastructure
* Database migrations

The framework handles a significant amount of common CRUD and infrastructure logic automatically.

```text
Model
  ↓
Serializer
  ↓
ModelViewSet
  ↓
Router
  ↓
REST API
```

**Project-level insight:** Django reduces application-level boilerplate by providing more functionality out of the box. This can improve development productivity when the application follows conventional CRUD-oriented patterns.

---

## FastAPI — Explicitness, Type Safety, and Asynchronous Execution

The FastAPI implementation had the largest code footprint at approximately **450 lines**. The additional code was primarily associated with explicitly defining:

* Pydantic v2 schemas
* API routes
* Dependency injection
* Async database sessions
* Authentication helpers
* Response models

This results in a more explicit API structure and makes request and response contracts highly visible in the code.

```text
Request
   ↓
FastAPI Router
   ↓
Pydantic Validation
   ↓
Dependency Injection
   ↓
Async SQLAlchemy
   ↓
Database
```

FastAPI also provides automatic OpenAPI schema generation and Swagger documentation.

In the Locust workload used in this project, the FastAPI implementation recorded the **highest observed concurrency throughput** among the three implementations.

**Project-level insight:** FastAPI trades some additional explicit application code for strong type-driven validation, automatic API documentation, dependency injection, and an asynchronous execution model.

---

## Flask — Minimalism and Architectural Control

The Flask implementation contained approximately **370 lines**.

Unlike Django, Flask provides fewer built-in application-level abstractions. The implementation therefore required explicit integration of:

* SQLAlchemy
* Marshmallow
* JWT authentication
* Input validation
* Route handling
* Database operations

```text
Flask
  │
  ├── SQLAlchemy
  ├── Marshmallow
  ├── PyJWT
  ├── Validation
  └── Application Logic
```

**Project-level insight:** Flask provides a minimal foundation and leaves more architectural decisions to the developer. This increases implementation responsibility but also provides granular control over the individual components.

---

# Abstraction vs Explicitness vs Control

The three implementations illustrate different architectural philosophies:

| Framework                 | Primary Project-Level Characteristic                  |
| ------------------------- | ----------------------------------------------------- |
| **Django REST Framework** | Abstraction and productivity                          |
| **FastAPI**               | Explicitness, type safety, and asynchronous execution |
| **Flask**                 | Minimalism and architectural control                  |

The difference in code size also illustrates an important trade-off:

```text
Higher Framework Abstraction
          ↓
Less Application Boilerplate

More Explicit Application Code
          ↓
Greater Visibility and Control
```

Therefore, a smaller codebase should not automatically be interpreted as a simpler or better architecture. In this project, Django's smaller footprint resulted partly from functionality being provided by the framework, while FastAPI's larger footprint resulted partly from explicitly defining schemas, dependencies, authentication, and database interactions.

---

# Framework Defaults and API Behavior

One of the most important findings from the parity testing was that **identical business requirements can produce different API behavior because of framework defaults**.

For example, duplicate user registration initially produced:

```text
Django REST Framework → HTTP 400
FastAPI               → HTTP 409
Flask                 → HTTP 409
```

Similarly, attempting to access a board owned by another user initially produced different authorization responses:

```text
Django → HTTP 404
Others → HTTP 403
```

Django therefore required explicit customization to match the API contract used by the other implementations.

These differences demonstrate why framework comparisons should evaluate more than raw performance. API behavior, validation defaults, error handling, abstractions, and developer control are also important dimensions.

---

# Key Lessons from the Benchmark

The benchmark demonstrates that framework selection involves several trade-offs rather than a single performance metric.

### Django REST Framework

Provides a high level of abstraction and reduces boilerplate through integrated ORM, serializers, routing, authentication, and CRUD functionality.

### FastAPI

Provides an explicit, type-driven API development model with automatic documentation and asynchronous execution capabilities.

### Flask

Provides a minimal foundation and allows developers to choose and integrate the components required by the application.

Overall, this project demonstrates that the meaningful difference between these frameworks is not simply **"which one is faster?"**, but rather:

> **How much does the framework abstract, how explicit is the application code, and how much architectural control remains with the developer?**

These observations are based on the implementations, parity tests, code footprint, and Locust workloads in this repository and should not be treated as universal rankings of the frameworks.
