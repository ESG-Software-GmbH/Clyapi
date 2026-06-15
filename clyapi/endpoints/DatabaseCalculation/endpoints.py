import requests
import json
import time
from clyapi.client import Client


def get_validation_status_count(client: Client, calculation_type: str, entity_id: str, use_pcaf_database: bool) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ValidationInfo/{calculation_type}/ValidationStatusCountList?usePCAFDatabase={str(use_pcaf_database).lower()}"
    headers = client.get_json_header()
    headers["EntityId"] = entity_id
    return requests.get(url, headers=headers, verify=True)


def get_validation_list_of_items(client: Client, validation_type: str, entity_id: str, validity: str, page_index: int, page_size: int) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ValidationInfo/{validation_type}/ListOfItems?validity={validity}&pageIndex={page_index}&pageSize={page_size}"
    headers = client.get_json_header()
    headers["EntityId"] = entity_id
    return requests.get(url, headers=headers, verify=True)


def get_validation_list_of_items_download(client: Client, validation_type: str, entity_id: str, validity: str, save_path: str | None = None) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ValidationInfo/{validation_type}/ListOfItems/Download?validity={validity}"
    headers = client.get_batch_header()
    headers["EntityId"] = entity_id
    response = requests.get(url, headers=headers, verify=True)
    if response.status_code == 200 and save_path:
        with open(save_path, "wb") as f:
            f.write(response.content)
    return response


def schedule_database_calculation(client: Client, calculation_name: str, calculation_type: str, entity_id: str, score_preset: str, result_unit: str, use_pcaf_database: bool) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ScheduleDatabaseCalculation"
    headers = client.get_json_header()
    headers["EntityId"] = entity_id
    payload = {
        "calculationName": calculation_name,
        "calculationType": calculation_type,
        "scorePresetCode": score_preset,
        "resultUnit": result_unit,
        "usePCAFDatabase": use_pcaf_database,
    }
    return requests.post(url, headers=headers, json=payload, verify=True)


def get_details_of_database_calculation(client: Client, calculation_id: str, entity_id: str) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ScheduleDatabaseCalculation/{calculation_id}"
    headers = client.get_json_header()
    headers["EntityId"] = entity_id
    return requests.get(url, headers=headers, verify=True)


def get_result_files_csv(client: Client, result_file_id: str, save_path: str | None = None) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/Download/ResultFileCSV/?resultFileId={result_file_id}"
    headers = client.get_batch_header()
    response = requests.get(url, headers=headers, verify=True)
    if response.status_code == 200 and save_path:
        with open(save_path, "wb") as f:
            f.write(response.content)
    return response


def run_database_calculation(
    client: Client,
    calculation_name: str,
    calculation_type: str,
    entity_id: str,
    score_preset: str,
    result_unit: str,
    use_pcaf_database: bool,
    poll_interval: int = 5,
) -> requests.Response:
    response = schedule_database_calculation(
        client, calculation_name, calculation_type, entity_id, score_preset, result_unit, use_pcaf_database
    )
    response.raise_for_status()
    calculation_id = response.json()["calculationId"]

    t0 = time.time()
    details = get_details_of_database_calculation(client, calculation_id, entity_id)
    status = details.json()["status"]
    while status == "InProgress":
        time.sleep(poll_interval)
        details = get_details_of_database_calculation(client, calculation_id, entity_id)
        status = details.json()["status"]

    print(f"Database calculation completed in {time.time() - t0:.1f}s with status: {status}")
    return details


if __name__ == "__main__":
    client = Client("Dev", "stress-testing")
    result = run_database_calculation(
        client,
        calculation_name="test_calc",
        calculation_type="PCR",
        entity_id="INITPERF",
        score_preset="DEFAULT",
        result_unit="EUR",
        use_pcaf_database=True,
    )
    print(result.json())
