# Infrastructure Deployment

This directory contains Azure Bicep templates for deploying the GitHub Spec Kit Demo application.

## Architecture Overview

The deployment creates the following Azure resources:

- **App Service Plan**: Linux-based hosting for the Flask application
- **App Service (Web App)**: Python 3.11 runtime with Gunicorn
- **Application Insights**: Telemetry and monitoring
- **Log Analytics Workspace**: Centralized logging

## Prerequisites

1. **Azure CLI** installed and configured
   ```bash
   az --version
   az login
   ```

2. **Bicep CLI** (included with Azure CLI 2.20.0+)
   ```bash
   az bicep version
   ```

3. **Resource Group** created for deployment
   ```bash
   az group create --name rg-speckit-demo-dev --location eastus
   ```

## Deployment

### Development Environment

```bash
# Deploy to development
az deployment group create \
  --resource-group rg-speckit-demo-dev \
  --template-file main.bicep \
  --parameters parameters/dev.bicepparam
```

### Production Environment

```bash
# Deploy to production
az deployment group create \
  --resource-group rg-speckit-demo-prod \
  --template-file main.bicep \
  --parameters parameters/prod.bicepparam
```

### Using What-If

Preview changes before deploying:

```bash
az deployment group what-if \
  --resource-group rg-speckit-demo-dev \
  --template-file main.bicep \
  --parameters parameters/dev.bicepparam
```

## Configuration

### Environment Parameters

| Parameter | Dev | Prod | Description |
|-----------|-----|------|-------------|
| `environment` | dev | prod | Environment name |
| `appName` | speckit-demo | speckit-demo | Base name for resources |
| `appServicePlanSku` | B1 | P1v3 | App Service Plan tier |

### App Settings

The following app settings are configured automatically:

| Setting | Description |
|---------|-------------|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights connection |
| `FLASK_ENV` | Flask environment (development/production) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | Enable build during deployment |

## Directory Structure

```
infra/
├── main.bicep              # Main template
├── README.md               # This file
├── modules/
│   ├── app-service.bicep   # App Service module
│   └── app-insights.bicep  # Application Insights module
└── parameters/
    ├── dev.bicepparam      # Development parameters
    └── prod.bicepparam     # Production parameters
```

## Outputs

After deployment, the following outputs are available:

| Output | Description |
|--------|-------------|
| `webAppUrl` | URL of the deployed application |
| `webAppName` | Name of the Web App resource |
| `appInsightsConnectionString` | Connection string for telemetry |

### Retrieve Outputs

```bash
az deployment group show \
  --resource-group rg-speckit-demo-dev \
  --name main \
  --query properties.outputs
```

## Application Deployment

After infrastructure is deployed, deploy the application:

```bash
# Package the application
cd ..
zip -r app.zip backend frontend

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group rg-speckit-demo-dev \
  --name speckit-demo-dev-app \
  --src app.zip
```

Or use the GitHub Actions workflow for automated deployments.

## Cleanup

```bash
# Delete development resources
az group delete --name rg-speckit-demo-dev --yes

# Delete production resources
az group delete --name rg-speckit-demo-prod --yes
```

## Troubleshooting

### View Deployment Logs

```bash
az webapp log tail \
  --resource-group rg-speckit-demo-dev \
  --name speckit-demo-dev-app
```

### Check Application Health

```bash
curl https://speckit-demo-dev-app.azurewebsites.net/api/health
```

### Application Insights

View application telemetry in the Azure Portal:
1. Navigate to Application Insights resource
2. View Live Metrics, Failures, Performance tabs
