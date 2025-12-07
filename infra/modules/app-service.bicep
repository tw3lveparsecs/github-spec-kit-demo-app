// App Service Bicep Module
// Deploys Azure App Service Plan and Web App for Python Flask application

@description('Name of the App Service Plan')
param appServicePlanName string

@description('Name of the Web App')
param webAppName string

@description('Azure region for deployment')
param location string

@description('SKU for App Service Plan')
param appServicePlanSku string

@description('Application Insights connection string')
@secure()
param appInsightsConnectionString string

@description('Application Insights instrumentation key')
@secure()
param appInsightsInstrumentationKey string

@description('Environment name')
param environment string

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: appServicePlanSku
  }
  properties: {
    reserved: true // Required for Linux
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'gunicorn --bind=0.0.0.0 --timeout 600 --chdir backend/src app:app'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      alwaysOn: environment == 'prod'
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsightsInstrumentationKey
        }
        {
          name: 'FLASK_ENV'
          value: environment == 'prod' ? 'production' : 'development'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
      ]
    }
  }
}

// Outputs
@description('The URL of the deployed web application')
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'

@description('The name of the deployed web application')
output webAppName string = webApp.name

@description('The principal ID of the Web App managed identity')
output webAppPrincipalId string = webApp.identity.principalId
