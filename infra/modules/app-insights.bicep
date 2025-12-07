// Application Insights Bicep Module
// Deploys Application Insights for monitoring and telemetry

@description('Name of the Application Insights resource')
param name string

@description('Azure region for deployment')
param location string

@description('Resource ID of the Log Analytics Workspace')
param logAnalyticsWorkspaceId string

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
    WorkspaceResourceId: logAnalyticsWorkspaceId
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    RetentionInDays: 30
  }
}

// Outputs
@description('The connection string for Application Insights')
output connectionString string = appInsights.properties.ConnectionString

@description('The instrumentation key for Application Insights')
output instrumentationKey string = appInsights.properties.InstrumentationKey

@description('The resource ID of Application Insights')
output id string = appInsights.id
