import requests
import time
import clyapi
from clyapi.client import  Client


def initial_import(client, counterpartyFile, transactionFile, itemFile):
    t0 = time.time()
    response = full_import_files(client, counterpartyFile, transactionFile, itemFile)
    operation_id = response.json()["operationId"]
    status = "IN_PROGRESS"
    while status == "IN_PROGRESS":
        time.sleep(1)
        status = full_import_status(client, operation_id).json()["status"]
    t1 = time.time()
    print(f"Import completed in {t1 - t0} seconds with Status: {status}")



def full_import_files(client: Client, counterpartyFile, transactionFile, itemFile) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3/Import/ImportInitialFromFile"
    headers = client.get_batch_header()
    payload = {}
    files = [
        ('counterpartyFile',
         ('ImportCounterparty.csv', open(counterpartyFile, 'rb'),
          'text/csv')
         ),
        ('transactionFile',
         ('ImportTransaction.csv', open(transactionFile, 'rb'),
          'text/csv')
         ),
        ('itemFile',
         ('ImportTransactionItem.csv', open(itemFile, 'rb'),
          'text/csv')
         )
    ]
    response = requests.request("POST", url, data=payload, files=files, headers=headers, verify=True)

    return response

# ------------------------------
''' Returns the status of the import operation. This includes counts of created, updated and deleted elements, and any validation errors. '''
# ------------------------------

def full_import_status(client, resultId) -> requests.Response:
    """
        Retrieves the import results by provided resultId ID.
        """
    url = f"{client.institution.url_prefix}/v3/Import/ImportResult/" + resultId

    headers = client.get_batch_header()

    response = requests.request("GET", url, headers=headers, verify=True)

    return response


if __name__ == '__main__':
    client: Client = Client("Dev", "stress-testing")
    # print(client)
    # print(clyapi.endpoints.Institution.institution_info(client))
    cp_path = "stress_tests/endpoint_tests/caches/initial_import_files/cp.csv"
    ta_path = "stress_tests/endpoint_tests/caches/initial_import_files/ta.csv"
    it_path = "stress_tests/endpoint_tests/caches/initial_import_files/it.csv"
    initial_import(client, cp_path, ta_path, it_path)


