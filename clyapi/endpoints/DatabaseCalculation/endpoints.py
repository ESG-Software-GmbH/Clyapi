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


def schedule_database_calculation(
    client: Client,
    calculation_name: str,
    calculation_type: str,
    entity_id: str,
    score_preset: str | None = None,
    result_unit: str | None = None,
    use_pcaf_database: bool | None = None,
    gar_version: str | None = None,
    is_monetary_effects: bool | None = None,
    monetary_fields: str | None = None,
    filter: str | None = None,
    reference_date: str | None = None,
) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ScheduleDatabaseCalculation"
    headers = client.get_json_header()
    if entity_id:
        headers["EntityId"] = entity_id
    payload = {"calculationName": calculation_name, "calculationType": calculation_type}
    # Only include optional fields when explicitly provided — avoids sending null
    # for fields the API treats as required for other calculation types.
    optional = {
        "scorePresetCode": score_preset,
        "resultUnit": result_unit,
        "usePCAFDatabase": use_pcaf_database,
        "garVersion": gar_version,
        "isMonetaryEffects": is_monetary_effects,
        "monetaryFields": monetary_fields,
        "filter": filter,
        "referenceDate": reference_date,
    }
    payload.update({k: v for k, v in optional.items() if v is not None})
    return requests.post(url, headers=headers, json=payload, verify=True)


def get_details_of_database_calculation(client: Client, calculation_id: str, entity_id: str | None = None) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/DatabaseCalculation/ScheduleDatabaseCalculation/{calculation_id}"
    headers = client.get_json_header()
    if entity_id:
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
    entity_id: str | None = None,
    poll_interval: int = 5,
    **optional_fields,
) -> requests.Response:
    response = schedule_database_calculation(
        client, calculation_name, calculation_type, entity_id, **optional_fields
    )
    response.raise_for_status()
    calculation_id = response.json()["calculationId"]

    t0 = time.time()
    details = get_details_of_database_calculation(client, calculation_id, entity_id)
    status = details.json()["status"]
    while status == "IN_PROGRESS" or status == "PREPARING":
        time.sleep(poll_interval)
        details = get_details_of_database_calculation(client, calculation_id, entity_id)
        status = details.json()["status"]

    print(f"Database calculation '{calculation_name}' completed in {time.time() - t0:.1f}s with status: {status}")
    return details


if __name__ == "__main__":
    client = Client("Dev", "stress-testing")
    result = run_database_calculation(
        client,
        calculation_name="smoke_pcr",
        calculation_type="PCR",
        # entity_id="strt1",
    )
    print(result.json())
