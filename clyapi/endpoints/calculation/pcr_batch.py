from clyapi.client import Client
import pandas as pd
import requests
import time
import csv
from io import StringIO
import os


def call_batch_upload_endpoint(client, csv_path, preset=None, calculation_type=None, result_unit=None):
    """Upload batch file to ScheduleBatchFile endpoint."""
    url = f"{client.institution.url_prefix}/api/v3.5/Calculation/ScheduleBatchFile"
    payload = {}
    if preset:
        payload["scorePresetCode"] = preset
    if calculation_type:
        payload["calculationType"] = calculation_type


    # file_dict = {os.path.basename(csv_path): csv_path}
    # files = [("files", (key, open(value, "rb"), "text/csv")) for key, value in file_dict.items()]
    # files = {"files": open(csv_path, "rb")}
    with open(csv_path, "rb") as f:
        files = {"files": (csv_path, f, "text/csv")}

        print("Uploading to:", url)
        print(payload)
        response = requests.post(url, headers=client.headers, json=payload, files=files, verify=False)
    print(response)
    return response


def physical_climate_risks_batch(client: Client, input_filepath: str, separator: str = ",", score_preset:str = None):
    """

    Parameters
    ----------
    client: clyapi.client.Client
        clyapi client for authentification
    input_filepath: str
        Local filepath of the input .csv file. Column specification can be read from the Climcycle data requirements
    separator: str
        Optional CSV separator, defaults to ",".
    score_preset: str
        Preset of PCR scoring preset. Defaults to Climcycle Default Preset
    Returns
    -------
    output_filepath: str
    """
    url_prefix = client.institution.url_prefix
    schedule_url = f"{url_prefix}/api/v3.5/Calculation/ScheduleBatchFile"
    result_info_url = f"{url_prefix}/api/v3.5/Calculation/ResultFilesInfo"
    download_csv_url = f"{url_prefix}/api/v3.5/Download/ResultFileCSV"


    payload = {}
    # if score_preset:
    # payload["scorePresetCode"] = score_preset
    payload["calculationType"] = "ESG"

    file_dict = {os.path.basename(input_filepath): input_filepath}
    files = [("files", (key, open(value, "rb"), "text/csv")) for key, value in file_dict.items()]

    print("Uploading to:", schedule_url)
    response = requests.post(schedule_url, headers=client.headers, data=payload, files=files, verify=True)
    print(response)
    print(response.json())

    max_wait = 60
    interval = 5
    waited = 0
    result_file_id = None

    while waited < max_wait:
        result_response = requests.get(result_info_url, headers=client.headers, params={"calculationId": calc_id})
        assert result_response.status_code == 200
        result_data = result_response.json()
        if result_data.get("resultFiles"):
            result_file_id = result_data["resultFiles"][0]["id"]
            break
        time.sleep(interval)
        waited += interval

    assert result_file_id

    waited = 0
    csv_content = None

    while waited < max_wait:
        download_response = requests.get(download_csv_url, headers=client.headers, params={"resultFileId": result_file_id})
        if download_response.status_code == 200:
            csv_content = download_response.content.decode("utf-8")
            break
        elif download_response.status_code == 202:
            time.sleep(interval)
            waited += interval
        else:
            download_response.raise_for_status()

    assert csv_content

    csv_reader = csv.reader(StringIO(csv_content))
    rows = list(csv_reader)
    header = rows[0]
    first_row = rows[1]

if __name__ == "__main__":
    import numpy as np
    import pandas as pd

    num = 10
    test_dict = {
        "Counterparty_ID": np.arange(0,num).astype(str),
        "Transaction_ID": np.arange(0,num).astype(str),
        "Item_ID": np.arange(0,num).astype(str),
        "Item_Longitude": np.linspace(10,15,num),
        "Item_Latitude": np.linspace(40,45, num),
        "Item_Origination_Date": "2025-01-01",
        "Item_Maturity_Date": "2055-01-01",
        "GCA": 100.0,
        "GCA_Share": 1.0,
        "Item_Nace_Code": "D 35.11"
    }
    file_path = "/Users/leonardmueller/Documents/git/Clyapi/clyapi/endpoints/calculation/pcr_input.csv"
    file_path = "/Users/leonardmueller/Documents/Physical_Climate_Risks_Template.csv"
    # df = pd.DataFrame(test_dict)
    # df.to_csv(file_path, index=False)

    client = Client("Stark Bank")
    print(client)
    # physical_climate_risks_batch(client, file_path)
    call_batch_upload_endpoint(client,file_path, calculation_type="PCR")
