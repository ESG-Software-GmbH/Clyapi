import requests
import json
import time
from clyapi.client import Client


def perform_differential_export(client: Client, to_file: bool, export_file_location: str, export_file_prefix: str) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.3/Export/ExportDifferential"
    headers = client.get_json_header()
    payload = json.dumps({
        "exportToFile": to_file,
        "exportFileLocation": export_file_location,
        "exportFilePrefix": export_file_prefix
    })
    return requests.post(url, headers=headers, data=payload, verify=True)


def get_export_status(client: Client, operation_id: str) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3/Export/ExportResult/{operation_id}"
    headers = client.get_json_header()
    return requests.get(url, headers=headers, verify=True)


def get_diff_export_data(client: Client, operation_id: str, limit: int = 10000) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3/Export/ExportResult/{operation_id}/Data?limit={limit}"
    headers = client.get_json_header()
    return requests.get(url, headers=headers, verify=True)


def set_last_export_time(client: Client, reset_time: str) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3/Export/ResetExportTime"
    headers = client.get_json_header()
    payload = json.dumps({"resetTime": reset_time})
    return requests.post(url, headers=headers, data=payload, verify=True)


def export_document(client: Client, document_id: str) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/Export/ExportDocument/{document_id}"
    headers = client.get_batch_header()
    return requests.get(url, headers=headers, verify=True)


def export_complete_data(client: Client) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/Export/ExportComplete"
    headers = client.get_json_header()
    return requests.post(url, headers=headers, verify=True)


def download_complete_data(client: Client, operation_id: str, timeout_minutes: int = 2) -> requests.Response:
    url = f"{client.institution.url_prefix}/v3.5/Export/ExportComplete/{operation_id}/Download"
    headers = client.get_batch_header()

    total_wait = 0
    while total_wait < timeout_minutes * 60:
        response = requests.get(url, headers=headers, stream=True, verify=True)
        if response.status_code == 200:
            return response
        time.sleep(60)
        headers = client.get_batch_header()
        total_wait += 60

    raise TimeoutError(f"Timed out waiting for export {operation_id} to be ready for download.")


def export_and_download_complete(client: Client, save_path: str | None = None, timeout_minutes: int = 300) -> requests.Response:
    response = export_complete_data(client)
    response.raise_for_status()
    operation_id = response.json()["operationId"]

    download_response = download_complete_data(client, operation_id, timeout_minutes=timeout_minutes)

    if save_path:
        with open(save_path, "wb") as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)

    return download_response


if __name__ == "__main__":
    client = Client("Dev", "stress-testing")
    export_and_download_complete(client,)
    # export_and_download_complete(client, "export.zip")