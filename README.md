# DivePlanWeb
**Webova aplikace pro evidenci, analyzu a planovani potapecskych ponoru.**

## Technologie

- **Backend** Python 3.13, Flask 3.1, Flask-Smorest, SQLAlchemy 2, Alembic, gunicorn
- **Frontend** React 19, TypeScript, Vite, Tailwind CSS v4, nginx (reverzní proxy)
- **Databáze** PostgreSQL 16
- **Auth** Flask-JWT-Extended, Werkzeug.security (pbkdf2:sha256)
- **Kontejnery** Docker, Docker Compose, python:3.13-slim, nginx:alpine
- **Cloudove nasazeni** Microsoft Azure, App Service (Linux Containers), PostgreSQL Flexible Server, ACR
- **Infrastruktura jako kod** ARM šablona (infra/main.json)
- **API dokumentace**  Swagger UI (/api/docs/swagger), OpenAPI 3.0


## Struktura projektu

```
DivePlanWeb/
├── backend/                    # Flask API server
│   ├── app/
│   │   ├── api/routes/         # REST endpointy (blueprinty)
│   │   ├── models/             # SQLAlchemy modely
│   │   ├── schemas/            # Marshmallow schémata
│   │   ├── planner/            # Kalkulacky a planner
│   │   ├── services/           # Servis sluzby
│   │   └── utils/              # Utility (jednotky, enumy, JWT helper)
│   ├── migrations/             # Alembic migrace
│   ├── tests/                  # Pytest testy
│   ├── Dockerfile              # Docker image (python:3.13-slim)
│   ├── start.sh                # Startup skript (DB migrace + gunicorn)
│   └── requirements.txt        # Pozadavky
│
├── frontend/
│   ├── react-app/
│   │   ├── src/
│   │   │   ├── components/     # UI komponenty + Layout + Navbar
│   │   │   ├── pages/          # Stránky (dives, planner, stats, admin)
│   │   │   ├── contexts/       # AuthContext, ThemeContext
│   │   │   └── lib/            # axios instance, utility funkce
│   │   └── public/
│   │       └── locales/        # i18n preklady (cs, en)
│   ├── Dockerfile              # Produkční Docker image (nginx:alpine)
│   ├── nginx.conf.template     # nginx konfigurace (proxy /api/* -> backend)
│   └── docker-entrypoint.sh    # Startup skript (envsubst + nginx)
│
├── infra/
│   ├── main.json               # ARM sablona, IAC (AZURE)
│   └── parameters.json         # Vzor parametru ARM sablony
│
├── docs/                       # Dokumenty projektu
├── docker-compose.yml          # Vývojové prostředí (Flask dev server + Vite + PostgreSQL)
└── docker-compose.runtime.yml  # Produkcni prostredi
```

## Autor DivePlanWeb

- Hronek Jan
- diplomová práce

*Projekt je nekomercni a open-source. Slouzi k vzdělavacim a vyzkumnym ucelum.*
