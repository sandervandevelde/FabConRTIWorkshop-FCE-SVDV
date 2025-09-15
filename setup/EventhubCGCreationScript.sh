#Eventhub Consumer Group creation script

resourceGroup="FabConEurope2025RG"
namespaceName="fabconeurope2025ehnspremium"
eventHubName="loratelemetry"

for i in $(seq 1 110); do
  consumerGroupName="fabconuser$(printf "%03d" $i)"
    az eventhubs eventhub consumer-group create \
      --resource-group $resourceGroup \
      --namespace-name $namespaceName \
      --eventhub-name $eventHubName \
      --name $consumerGroupName
done

resourceGroup="FabConEurope2025RG"
namespaceName="fabconeurope2025ehnspremium"
eventHubName="factorytelemetry"

for i in $(seq 1 110); do
  consumerGroupName="fabconuser$(printf "%03d" $i)"
  az eventhubs eventhub consumer-group delete \
    --resource-group $resourceGroup \
    --namespace-name $namespaceName \
    --eventhub-name $eventHubName \
    --name $consumerGroupName
done