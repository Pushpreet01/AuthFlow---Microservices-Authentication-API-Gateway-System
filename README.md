# Backend

Dockerized FastAPI microservices backend for a badminton platform. The backend is organized around an API gateway, a user service, and an authentication service, with PostgreSQL as the persistence layer.

## Architecture

- `gateway/`: public API entrypoint, request forwarding, auth middleware, cookie-based session handling
- `auth/`: registration, login, password changes, JWT creation, refresh-token rotation
- `user/`: user creation, profile updates, lookup, deletion, reputation updates
- `db/migrations/`: database schema bootstrap SQL

## Services

- `api-gateway`
  - Runs on host port `5000`
  - Handles routing to internal services
  - Stores access and refresh tokens in HTTP-only cookies
- `auth-service`
  - Runs on host port `8000`
  - Manages password hashing, login, logout, refresh-token flow, and password changes
- `user-service`
  - Runs on host port `8001`
  - Manages user records and profile-related operations

## Implemented Features

- User signup flow split across services
- User login with JWT access token issuance
- Refresh-token generation, storage, invalidation, and rotation
- Password hashing using Argon2
- Password change flow
- User lookup by ID and email
- User profile update and delete
- User reputation increment and decrement
- FastAPI-based internal microservice communication with `httpx`
- PostgreSQL access through `psycopg` and async connection pooling
- Dockerfiles for each service and Docker Compose orchestration

## Database Scope

The current SQL schema includes implemented account/auth tables and planned product tables for:

- clubs
- rooms
- room participants
- reputation events
- points wallet and ledger
- money ledger

The account and auth flows are implemented in service code. The room, club, and wallet systems are currently schema-level groundwork and are not yet exposed as active service routes.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- Psycopg 3 / psycopg-pool
- HTTPX
- Python-JOSE
- Argon2
- Docker / Docker Compose

## Project Structure

```text
backend/
|-- auth/
|   |-- app/
|   |-- db/
|   |-- dockerfile
|   `-- requirements.txt
|-- gateway/
|   |-- app/
|   |-- dockerfile
|   `-- requirements.txt
|-- user/
|   |-- app/
|   |-- db/
|   |-- dockerfile
|   `-- requirements.txt
|-- db/
|   `-- migrations/
|-- docker-compose.yml
`-- README.md
```

## Environment Setup

Each service currently expects its own `.env` file:

- `auth/.env`
- `user/.env`
- `gateway/.env`

Do not commit real `.env` files. Replace them with `.env.example` files before publishing.

Typical variables used in the project:

```env
DB_USER=postgres
DB_PASSWORD=changeme
DB_HOST=localhost
DB_PORT=5432
DB_NAME=badminton

JWT_SECRET=replace_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

USER_SERVICE_URL=http://user-service:8000/users
AUTH_SERVICE_URL=http://auth-service:8000/auth
```

## Running Locally

1. Create service `.env` files or `.env.example` files with local values.
2. Make sure PostgreSQL is available and the target database exists.
3. Apply the SQL in `db/migrations/init.sql`.
4. Start the services:

```bash
docker compose up --build
```

5. Access the gateway at:

```text
http://localhost:5000
```

## Current Notes

- `docker-compose.yml` currently defines the three application containers but not a PostgreSQL container.
- Local `venv/`, `__pycache__/`, `.env`, and `volumes/` directories should be excluded from version control.
- This backend currently focuses on account/auth foundations; gameplay booking and wallet features are partially designed at the schema level.

## Resume-Oriented Summary

Built a Dockerized FastAPI microservices backend with an API gateway, dedicated authentication and user services, PostgreSQL persistence, JWT-based authentication, refresh-token rotation, HTTP-only cookie session handling, and profile/reputation management for a badminton platform.
