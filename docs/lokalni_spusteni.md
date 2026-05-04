# DivePlanWeb — Lokální spuštění

## Požadavky
| Nástroj | Účel |
|---------|------|
| **Git** | Klonování repozitáře |
| **Docker Desktop** | Kontejnerizace (backend, frontend, DB) |
| **VS Code** | IDE editor |
| **Dev Containers** (VS Code ext.) | Vývoj uvnitř kontejneru |


## 1) Stažení projektu z GitHubu
```bash
git clone https://github.com/<tvuj-ucet>/DivePlanWeb.git
cd DivePlanWeb
```

## 2) Konfigurace prostředí (`.env`)
V rootu projektu vytvoř soubor `.env` podle vzoru:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=zmen-toto-heslo
POSTGRES_DB=dive_plan_web_db
DATABASE_URL=postgresql://admin:zmen-toto-heslo@db:5432/dive_plan_web_db
FLASK_APP=run.py
FLASK_CONFIG=development
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=8000
```

## 3) Spuštění Docker Compose
Z rootu projektu (kde je `docker-compose.yml`):
### Pro sestaveni kontejneru
```bash
docker compose down -v
docker compose up -d --build
```
### Start kontejneru po zastaveni
```bash
docker compose up -d
```
### Ověření stavu kontejnerů
```bash
docker compose ps
docker ps
```
Měl bys videt:
- `dive_plan_web_backend` (port 8000)
- `dive_plan_web_frontend` (port 5173)
- `dive_plan_web_db` (port 5432)

## 4) VS Code Dev Containers
### Backend Dev Container
1. Otevři VS Code
2. **File -> Open Folder** -> vyber `DivePlanWeb/backend/`
3. VS Code zobrazí výzvu "Reopen in Container" -> potvrď
4. V terminálu kontejneru:
```bash
docker exec -it dive_plan_web_backend bash   # otevre backend kontejner
pip install -r requirements.txt         # stahne pozadavky
flask db upgrade                        # spusti migrace
flask db current                        # overi stav
flask run --host=0.0.0.0 --port=8000    # lokalni spusteni (ctrl+c = stop)
```

### Frontend Dev Container
1. Otevři druhé okno VS Code
2. **File -> Open Folder** -> vyber `DivePlanWeb/frontend/`
3. **Reopen in Container**
4. V terminálu kontejneru:
```bash
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

#### Frontend -> http://localhost:5173 
#### Backend -> http://localhost:8000 
#### Swagger UI -> http://localhost:8000/api/docs/swagger 
