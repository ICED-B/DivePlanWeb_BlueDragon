# DivePlanWeb — Nasazení na Microsoft Azure

***Předpoklad***
Docker Desktop spuštěný
Azure CLI nainstalovyný
Microsoft Azure subscription aktivní

## Vytvoření Resource Group a Container Registry v Azure Porálu

### a. Resource Group (RG)
- https://portal.azure.com -> **Resource groups** -> **Create**
- Vyplň:
    **Resource group name:** rg-diveplanweb
    **region:** Switzerland North
    **Review + create** -> Create

### b. Azure Container Registry (ACR)
- jdi do rg-diveplanweb -> **Create** -> najdi **Container Registry**
- vyplň:
    **Registry name:** diveplanweb
    **Location:** Switzerland North
    **Pricing plan:** Basic
    **Review + create** -> Create -> *Deployment succeeded*


## Build a push Docker images

otevři PowerShell a jdi do projektu -> cd DivePlanWeb

### prihlaseni do Azure a ACR
```powershell
az login
az account set --subscription
az acr login --name duveplanweb
```

### Build backendu
```powershell
docker build --no-cache -t diveplanweb.azurecr.io/dpw-backend:latest -f backend/Dockerfile.runtime ./backend
docker push diveplanweb.azurecr.io/dpw-backend:latest
```

### Build frontendu
```powershell
docker build --no-cache -t diveplanweb.azurecr.io/dpw-frontend:latest -f frontend/Dockerfile.runtime ./frontend
docker push diveplanweb.azurecr.io/dpw-frontend:latest
```


## Nasazení infrastruktury přes šablonu
ARM šablona v infra/main.json zbyle zdroje vytvoří automaticky

```powershell
az deployment group create `
  --resource-group rg-diveplanweb `
  --template-file infra/main.json `
  --parameters `
    location=switzerlandnorth `
    acrName=diveplanweb `
    acrResourceGroup=rg-diveplanweb `
    acrLoginServer=diveplanweb.azurecr.io `
    backendName=dpw-backend `
    frontendName=dpw-frontend `
    dbServerName=dpw-pg-server `
    dbAdminPassword="SILNÉ_HESLO_K_DB" `
    secretKey="NÁHODNÝ_TAJNÝ_KLÍČ_MIN_32_ZNAKŮ" `
    jwtSecretKey="NÁHODNÝ_JWT_KLÍČ_MIN_32_ZNAKŮ"
```

**ARM vytvoří**
1. App Service Plan (Linux, SKU B1)
2. PostgreSQL Flexible Server + databáze + firewall rule (`AllowAllWindowsAzureIps`)
3. Backend Web App nastavi: `WEBSITES_PORT=8000`, `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `FLASK_CONFIG=production`
4. Frontend Web App nastavi: `WEBSITES_PORT=80`, `BACKEND_URL=https://dpw-backend.azurewebsites.net`
5. Managed Identity (System-Assigned) + AcrPull role pro obě Web Apps


## timeout startu
Backend potrebuje vice casu pro start
```powershell
az webapp config appsettings set `
  --name dpw-backend `
  --resource-group rg-diveplanweb `
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=600
```

## RESTART
```powershell
az webapp restart --name dpw-backend --resource-group rg-diveplanweb
az webapp restart --name dpw-frontend --resource-group rg-diveplanweb
```

## Dotupne aresy v prohlizeci

Backend swagger: https://dpw-backend.azurewebsites.net/api/docs/swagger
Frontend app: https://dpw-frontend.azurewebsites.net
