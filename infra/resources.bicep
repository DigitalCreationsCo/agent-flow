@description('The location used for all deployed resources')
param location string = resourceGroup().location

@description('Tags that will be applied to all resources')
param tags object = {}


@secure()
param databasePassword string
param frontendExists bool
@secure()
param frontendDefinition object
param baseExists bool
@secure()
param baseDefinition object

@description('Id of the user or app to assign application roles')
param principalId string

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = uniqueString(subscription().id, resourceGroup().id, location)

// Monitor application with Azure Monitor
module monitoring 'br/public:avm/ptn/azd/monitoring:0.1.0' = {
  name: 'monitoring'
  params: {
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
    applicationInsightsDashboardName: '${abbrs.portalDashboards}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container registry
module containerRegistry 'br/public:avm/res/container-registry/registry:0.1.1' = {
  name: 'registry'
  params: {
    name: '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    acrAdminUserEnabled: true
    tags: tags
    publicNetworkAccess: 'Enabled'
    roleAssignments:[
      {
        principalId: frontendIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
      }
      {
        principalId: baseIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
      }
    ]
  }
}

// Container apps environment
module containerAppsEnvironment 'br/public:avm/res/app/managed-environment:0.4.5' = {
  name: 'container-apps-environment'
  params: {
    logAnalyticsWorkspaceResourceId: monitoring.outputs.logAnalyticsWorkspaceResourceId
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    zoneRedundant: false
  }
}
var databaseName = 'langflow'
var databaseUser = 'psqladmin'
module postgreServer 'br/public:avm/res/db-for-postgre-sql/flexible-server:0.1.4' = {
  name: 'postgreServer'
  params: {
    // Required parameters
    name: '${abbrs.dBforPostgreSQLServers}${resourceToken}'
    skuName: 'Standard_B1ms'
    tier: 'Burstable'
    // Non-required parameters
    administratorLogin: databaseUser
    administratorLoginPassword: databasePassword
    geoRedundantBackup: 'Disabled'
    passwordAuth:'Enabled'
    firewallRules: [
      {
        name: 'AllowAllIps'
        startIpAddress: '0.0.0.0'
        endIpAddress: '255.255.255.255'
      }
    ]
    databases: [
      {
        name: databaseName
      }
    ]
    location: location
  }
}

module frontendIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.2.1' = {
  name: 'frontendidentity'
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}frontend-${resourceToken}'
    location: location
  }
}

module frontendFetchLatestImage './modules/fetch-container-image.bicep' = {
  name: 'frontend-fetch-image'
  params: {
    exists: frontendExists
    name: 'frontend'
  }
}

var frontendAppSettingsArray = filter(array(frontendDefinition.settings), i => i.name != '')
var frontendSecrets = map(filter(frontendAppSettingsArray, i => i.?secret != null), i => {
  name: i.name
  value: i.value
  secretRef: i.?secretRef ?? take(replace(replace(toLower(i.name), '_', '-'), '.', '-'), 32)
})
var frontendEnv = map(filter(frontendAppSettingsArray, i => i.?secret == null), i => {
  name: i.name
  value: i.value
})

module frontend 'br/public:avm/res/app/container-app:0.8.0' = {
  name: 'frontend'
  params: {
    name: 'frontend'
    ingressTargetPort: 3000
    scaleMinReplicas: 1
    scaleMaxReplicas: 10
    secrets: {
      secureList:  union([
      ],
      map(frontendSecrets, secret => {
        name: secret.secretRef
        value: secret.value
      }))
    }
    containers: [
      {
        image: frontendFetchLatestImage.outputs.?containers[?0].?image ?? 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
        name: 'main'
        resources: {
          cpu: json('0.5')
          memory: '1.0Gi'
        }
        env: union([
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: monitoring.outputs.applicationInsightsConnectionString
          }
          {
            name: 'AZURE_CLIENT_ID'
            value: frontendIdentity.outputs.clientId
          }
          {
            name: 'BASE_BASE_URL'
            value: 'https://base.${containerAppsEnvironment.outputs.defaultDomain}'
          }
          {
            name: 'PORT'
            value: '3000'
          }
        ],
        frontendEnv,
        map(frontendSecrets, secret => {
            name: secret.name
            secretRef: secret.secretRef
        }))
      }
    ]
    managedIdentities:{
      systemAssigned: false
      userAssignedResourceIds: [frontendIdentity.outputs.resourceId]
    }
    registries:[
      {
        server: containerRegistry.outputs.loginServer
        identity: frontendIdentity.outputs.resourceId
      }
    ]
    environmentResourceId: containerAppsEnvironment.outputs.resourceId
    location: location
    tags: union(tags, { 'azd-service-name': 'frontend' })
  }
}

module baseIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.2.1' = {
  name: 'baseidentity'
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}base-${resourceToken}'
    location: location
  }
}

module baseFetchLatestImage './modules/fetch-container-image.bicep' = {
  name: 'base-fetch-image'
  params: {
    exists: baseExists
    name: 'base'
  }
}

var baseAppSettingsArray = filter(array(baseDefinition.settings), i => i.name != '')
var baseSecrets = map(filter(baseAppSettingsArray, i => i.?secret != null), i => {
  name: i.name
  value: i.value
  secretRef: i.?secretRef ?? take(replace(replace(toLower(i.name), '_', '-'), '.', '-'), 32)
})
var baseEnv = map(filter(baseAppSettingsArray, i => i.?secret == null), i => {
  name: i.name
  value: i.value
})

module base 'br/public:avm/res/app/container-app:0.8.0' = {
  name: 'base'
  params: {
    name: 'base'
    ingressTargetPort: 80
    corsPolicy: {
      allowedOrigins: [
        'https://frontend.${containerAppsEnvironment.outputs.defaultDomain}'
      ]
      allowedMethods: [
        '*'
      ]
    }
    scaleMinReplicas: 1
    scaleMaxReplicas: 10
    secrets: {
      secureList:  union([
        {
          name: 'db-pass'
          value: databasePassword
        }
        {
          name: 'db-url'
          value: 'postgresql://${databaseUser}:${databasePassword}@${postgreServer.outputs.fqdn}:5432/${databaseName}'
        }
        {
          name: 'redis-pass'
          identity:baseIdentity.outputs.resourceId
          keyVaultUrl: '${keyVault.outputs.uri}secrets/REDIS-PASSWORD'
        }
        {
          name: 'redis-url'
          identity:baseIdentity.outputs.resourceId
          keyVaultUrl: '${keyVault.outputs.uri}secrets/REDIS-URL'
        }
      ],
      map(baseSecrets, secret => {
        name: secret.secretRef
        value: secret.value
      }))
    }
    containers: [
      {
        image: baseFetchLatestImage.outputs.?containers[?0].?image ?? 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
        name: 'main'
        resources: {
          cpu: json('0.5')
          memory: '1.0Gi'
        }
        env: union([
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: monitoring.outputs.applicationInsightsConnectionString
          }
          {
            name: 'AZURE_CLIENT_ID'
            value: baseIdentity.outputs.clientId
          }
          {
            name: 'POSTGRES_HOST'
            value: postgreServer.outputs.fqdn
          }
          {
            name: 'POSTGRES_USERNAME'
            value: databaseUser
          }
          {
            name: 'POSTGRES_DATABASE'
            value: databaseName
          }
          {
            name: 'POSTGRES_PASSWORD'
            secretRef: 'db-pass'
          }
          {
            name: 'POSTGRES_URL'
            secretRef: 'db-url'
          }
          {
            name: 'POSTGRES_PORT'
            value: '5432'
          }
          {
            name: 'REDIS_HOST'
            value: redis.outputs.hostName
          }
          {
            name: 'REDIS_PORT'
            value: string(redis.outputs.sslPort)
          }
          {
            name: 'REDIS_URL'
            secretRef: 'redis-url'
          }
          {
            name: 'REDIS_ENDPOINT'
            value: '${redis.outputs.hostName}:${string(redis.outputs.sslPort)}'
          }
          {
            name: 'REDIS_PASSWORD'
            secretRef: 'redis-pass'
          }
          {
            name: 'PORT'
            value: '80'
          }
        ],
        baseEnv,
        map(baseSecrets, secret => {
            name: secret.name
            secretRef: secret.secretRef
        }))
      }
    ]
    managedIdentities:{
      systemAssigned: false
      userAssignedResourceIds: [baseIdentity.outputs.resourceId]
    }
    registries:[
      {
        server: containerRegistry.outputs.loginServer
        identity: baseIdentity.outputs.resourceId
      }
    ]
    environmentResourceId: containerAppsEnvironment.outputs.resourceId
    location: location
    tags: union(tags, { 'azd-service-name': 'base' })
  }
}
module redis 'br/public:avm/res/cache/redis:0.3.2' = {
  name: 'redisDeployment'
  params: {
    // Required parameters
    name: '${abbrs.cacheRedis}${resourceToken}'
    // Non-required parameters
    location: location
    skuName: 'Basic'
  }
}

module redisConn './modules/set-redis-conn.bicep' = {
  name: 'redisConn'
  params: {
    name: redis.outputs.name
    passwordSecretName: 'REDIS-PASSWORD'
    urlSecretName: 'REDIS-URL'
    keyVaultName: keyVault.outputs.name
  }
}
// Create a keyvault to store secrets
module keyVault 'br/public:avm/res/key-vault/vault:0.6.1' = {
  name: 'keyvault'
  params: {
    name: '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    enableRbacAuthorization: false
    accessPolicies: [
      {
        objectId: principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
      {
        objectId: frontendIdentity.outputs.principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
      {
        objectId: baseIdentity.outputs.principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
    ]
    secrets: [
      {
        name: 'db-pass'
        value: databasePassword
      }
    ]
  }
}
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_RESOURCE_FRONTEND_ID string = frontend.outputs.resourceId
output AZURE_RESOURCE_BASE_ID string = base.outputs.resourceId
output AZURE_RESOURCE_REDIS_ID string = redis.outputs.resourceId
output AZURE_RESOURCE_LANGFLOW_ID string = '${postgreServer.outputs.resourceId}/databases/langflow'
