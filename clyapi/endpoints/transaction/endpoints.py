import requests
from clyapi.header_builder import build_headers
from clyapi.client import Client
# ------------------------------
''' Fetches the Transaction Ids present in the system. '''


# ------------------------------

def get_transaction_ids(env_setup, limit=10000):
    url = f"{env_setup['api_url']}/v3/Transaction?limit=" + str(limit)

    headers = build_headers(env_setup)

    response = requests.request("GET", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Fetches the Transaction Ids present in the system grouped by Entity. '''


# ------------------------------

def get_transaction_ids_for_group(env_setup):
    url = f"{env_setup['api_url']}/v3.5/Transaction/ListTransactionsGroupedByEntity"
    headers = build_headers(env_setup)
    response = requests.request("GET", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Streams all Transaction Ids present in the system as a plaintext response where each transaction ID is returned on a new line. '''


# ------------------------------

def get_transaction_ids_as_stream(env_setup):
    url = f"{env_setup['api_url']}/v3/Transaction/StreamIds"

    headers = build_headers(env_setup)

    response = requests.request("GET", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Returns Transaction data for the requested Id. '''


# ------------------------------

def get_transaction_information(env_setup, transaction_id):
    url = f"{env_setup['api_url']}/v3/Transaction/" + transaction_id

    headers = build_headers(env_setup)

    response = requests.request("GET", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Create or update the Transaction with the provided field values. '''


# ------------------------------

def create_or_update_transaction(env_setup, transaction_id, payload):
    """ Payload is a dictionary of the following form:
        {
        "counterpartyId": null,
        "fields": {
            "GCA": 100000,
            "Maturity_Date": "2030-01-01T00:00:00",
            "Derivatives": true
            }
        } """

    url = f"{env_setup['api_url']}/v3/Transaction/" + transaction_id

    headers = build_headers(env_setup)

    response = requests.request("POST", url, headers=headers, data=payload, verify=True)

    return response


# ------------------------------
''' Delete the Transaction. All Items for the Transaction will be deleted as well. '''


# ------------------------------

def delete_transaction(env_setup, transaction_id):
    url = f"{env_setup['api_url']}/v3/Transaction/" + transaction_id

    headers = build_headers(env_setup)

    response = requests.request("DELETE", url, headers=headers, verify=True)

    return response


# ------------------------------
# ------------------------------
''' Item Endpoints '''
# ------------------------------
# ------------------------------


# ------------------------------
''' Returns Item data for the requested Id. '''


# ------------------------------

def get_item_information(env_setup, transaction_id, item_id):
    url = f"{env_setup['api_url']}/v3/Transaction/" + transaction_id + "/" + item_id

    headers = build_headers(env_setup)

    response = requests.request("GET", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Create or update the Item with the provided field values. '''


# ------------------------------

def create_or_update_item(env_setup, transaction_id, item_id, payload):
    """ Payload is a dictionary of the following form:
        {
        "fields": {
            "GCA_Share": 100000,
            "Item_NACE_Code": "A 01",
            "Item_Country_Code": "DEU"
            }
        } """

    url = f"{env_setup['api_url']}/v3/Transaction/" + transaction_id + "/" + item_id

    headers = build_headers(env_setup)

    response = requests.request("POST", url, headers=headers, data=payload, verify=True)

    return response


# ------------------------------
''' Delete Item '''


# ------------------------------

def delete_item(env_setup, transaction_id, item_id):
    url = f"{env_setup['api_url']}/v3/Transaction/" + transaction_id + "/" + item_id

    headers = build_headers(env_setup)

    response = requests.request("DELETE", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Returns Calculation result data of the requested type. '''


# ------------------------------

def get_calculation_results(env_setup, transactionId, itemId, calculationType):
    url = f"{env_setup['api_url']}/v3/Transaction/" + transactionId + "/" + itemId + "/" + calculationType

    headers = build_headers(env_setup)

    response = requests.request("GET", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Change the Transaction identifier. '''


# ------------------------------

def change_transaction_id(env_setup, transactionId_old, transactionId_new):
    url = f"{env_setup['api_url']}/v3.5/Transaction/" + transactionId_old + "/ChangeIdentifier?newTransactionId=" + transactionId_new

    headers = build_headers(env_setup)

    response = requests.request("PUT", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Change the Legal Entity for transaction.

    For an institution from a group with the Legal Entity v1.0 feature (unique transaction identifier per group), 
    it is enough to provide the parameters transactionId and newLegalEntityCode. 

    For an institution from a group with the Legal Entity v2.0 feature (unique transaction identifier per entity), 
    it is required to provide all parameters. '''


# ------------------------------

def change_entity_id_v1(env_setup, transaction_id, new_entity_id):
    url = f"{env_setup['api_url']}/v3.5/Transaction/" + transaction_id + "/ChangeLegalEntity?newLegalEntityCode=" + new_entity_id

    headers = build_headers(env_setup)

    response = requests.request("PUT", url, headers=headers, verify=True)

    return response


# ------------------------------
''' Change the Transaction Item identifier. '''


# ------------------------------

def change_item_id(env_setup, transactionId, item_Id_old, item_Id_new):
    url = (f"{env_setup['api_url']}/v3.5/Transaction/" + transactionId + "/" + item_Id_old +
           "/ChangeIdentifier?newItemId=" + item_Id_new)

    headers = build_headers(env_setup)

    response = requests.request("PUT", url, headers=headers, verify=True)

    return response

if __name__ == "__main__":
    client = Client("Dev", "Stark Bank")
    env_setup = client.get_legacy_env_setup()
    print(env_setup)
    ids = get_transaction_ids(env_setup, limit=10).json()
    print(ids)