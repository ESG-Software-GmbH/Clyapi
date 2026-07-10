from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient


def scale_elastic_pool(capacity):
    # Set your Azure subscription ID
    subscription_id = ""

    # Resource details
    resource_group_name = ""
    server_name = ""
    elastic_pool_name = ""

    # Initialize client
    credential = DefaultAzureCredential()
    sql_client = SqlManagementClient(credential, subscription_id)

    # load required original configurations
    existing_pool = sql_client.elastic_pools.get(resource_group_name, server_name, elastic_pool_name)
    current_storage = existing_pool.max_size_bytes

    # New configuration for the elastic pool (example: scale to Standard tier, 200 DTUs)
    elastic_pool_params = {
        "location": "West Europe",  # e.g., "eastus"
        "sku": {
            "name": "StandardPool",  # Check for correct name for your pricing tier
            "tier": "Standard",
            "capacity": capacity  # DTUs or vCores depending on pricing model
        },
        "per_database_settings": {
            "min_capacity": 0,  # Optional: minimum DTUs a database can use
            "max_capacity": capacity  # Set this to the desired max DTUs per database
        },
        "max_size_bytes": current_storage
    }

    # Update the elastic pool
    poller = sql_client.elastic_pools.begin_create_or_update(
        resource_group_name,
        server_name,
        elastic_pool_name,
        elastic_pool_params
    )

    result = poller.result()
    print(f"Elastic pool scaled. New SKU: {result.sku.name}, Capacity: {result.sku.capacity}")

if __name__ == "__main__":
    scale_elastic_pool(capacity=100)