import requests
import time
from clyapi.client import Client
import os


# ------------------------------
''' Schedules a batch calculation from a file. '''
# ------------------------------

def call_batch_upload_endpoint(client:Client, csv_path: str, preset: str =None, calculation_type: str=None, result_unit=None) -> dict:
    """Upload batch file to ScheduleBatchFile endpoint."""
    url = f"{client.institution.url_prefix}/api/v3.5/Calculation/ScheduleBatchFile"
    payload = {}
    if preset:
        payload["scorePresetCode"] = preset
    if calculation_type:
        payload["calculationType"] = calculation_type


    with open(csv_path, "rb") as f:
        files = [("files", (os.path.split(csv_path)[-1], f, "text/csv"))]
        response = requests.post(url, headers=client.get_batch_header(), data=payload, files=files, verify=True)
    if response.status_code == 400:
        raise ValueError(response.json())
    if response.status_code != 200:
       raise ConnectionError(response.json())

    return response.json()


# ------------------------------
''' Returns information about type of calculation and calculation result files for specified calculation Id. '''
# ------------------------------


def get_result_files_info(client: Client, calculation_id, max_attempts=30, wait_seconds=5):
    """Poll ResultFilesInfo until results are available or timeout."""
    url = f"{client.institution.url_prefix}/v3.5/Calculation/ResultFilesInfo"
    params = {"calculationId": calculation_id}

    for attempt in range(1, max_attempts + 1):
        print(f"Waiting for calculation, polling attempt {attempt}/{max_attempts}...", end="\r")
        response = requests.get(url, headers=client.get_batch_header(), params=params, verify=True)

        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                print("Failed to parse ResultFilesInfo response")
                print(response.text)
                return None

            if data.get("resultFiles"):
                print("Result files available!")
                return data
            else:
                print("Still processing, waiting...")
        elif response.status_code == 404:
            pass
            # print("Polling attempt {attempt}/{max_attempts}... Calculation not ready yet (404). Waiting...", end="\r")
        else:
            print(f"Unexpected status {response.status_code}: {response.text}")
            break

        time.sleep(wait_seconds)

    raise TimeoutError(f"Max attempts reached, results not ready. Try checking for calculation results later with the calculation id: \n {calculation_id}"
            f"\n via clyapi.endpoints.calculation.calculation_utils.get_result_files_info()"
            f"\n and clyapi.endpoint.calculation.calculation_utls.get_result_file_csv()")

def get_result_file_csv(client: Client, result_file_id):
    print(f"downloading result file with id: {result_file_id}", end="\r")

    url = f"{client.institution.url_prefix}/v3/Download/ResultFileCSV?resultFileId=" + result_file_id
    response = requests.request("GET", url, headers=client.get_json_header(), verify=True)

    print(f"successfully downloaded result file with id: {result_file_id}")

    return response
