// Main Bicep template for GitHub Spec Kit Demo Application
// Deploys Azure App Service and Application Insights

@description('Environment name - used for resource naming')
@allowed([
  'dev'
  'prod'
])
param environment string = 'dev'

@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Base name for resources')
param appName string = 'speckit-demo'

@description('SKU for App Service Plan')
param appServicePlanSku string = environment == 'prod' ? 'P1v3' : 'B1'

// Variables
var resourcePrefix = '${appName}-${environment}'
var appServicePlanName = '${resourcePrefix}-plan'
var webAppName = '${resourcePrefix}-app'
var appInsightsName = '${resourcePrefix}-insights'
var logAnalyticsName = '${resourcePrefix}-logs'

// Log Analytics Workspace for Application Insights
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
module appInsights 'modules/app-insights.bicep' = {
  name: 'appInsights'
  params: {
    name: appInsightsName
    location: location
    logAnalyticsWorkspaceId: logAnalytics.id
  }
}

// App Service
module appService 'modules/app-service.bicep' = {
  name: 'appService'
  params: {
    appServicePlanName: appServicePlanName
    webAppName: webAppName
    location: location
    appServicePlanSku: appServicePlanSku
    appInsightsConnectionString: appInsights.outputs.connectionString
    appInsightsInstrumentationKey: appInsights.outputs.instrumentationKey
    environment: environment
  }
}

// Outputs
@description('The URL of the deployed web application')
output webAppUrl string = appService.outputs.webAppUrl

@description('The name of the deployed web application')
output webAppName string = appService.outputs.webAppName

@description('Application Insights connection string')
output appInsightsConnectionString string = appInsights.outputs.connectionString
