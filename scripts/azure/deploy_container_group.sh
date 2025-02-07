az login

az group create --name agentflowcg --location centralus

az container create --resource-group agentflowcapp --file deploy/deploy.azure.yml

az container show --resource-group agentflowcapp --name agentflowcg --output table