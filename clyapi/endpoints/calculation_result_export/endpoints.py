import requests
import time
from clyapi.client import Client

# Status strings (case-insensitive) that indicate the export is not yet ready.
IN_PROGRESS_STATUSES = {"IN_PROGRESS", "INPROGRESS", "PREPARING", "PENDING", "QUEUED", "SCHEDULED"}


def schedule_calculation_result_export(client: Client, calculation_type: str, recent: bool = False) -> requests.Response:
    """Schedule the export of calculation results for a given calculation type."""
    url = f"{client.institution.url_prefix}/v3.5/CalculationResultExport/ExportResults"
    headers = client.get_json_header()
    params = {"calculationType": calculation_type, "recent": str(recent).lower()}
    return requests.get(url, headers=headers, params=params, verify=True)


def get_calculation_result_export_status(client: Client, operation_id: str) -> requests.Response:
    """Fetch the status of a scheduled calculation result export."""
    url = f"{client.institution.url_prefix}/v3.5/CalculationResultExport/ExportResult/{operation_id}"
    headers = client.get_json_header()
    return requests.get(url, headers=headers, verify=True)


def download_calculation_result_export_file(client: Client, operation_id: str, save_path: str | None = None) -> requests.Response:
    """Retrieve the raw result file produced by a calculation result export."""
    url = f"{client.institution.url_prefix}/v3.5/CalculationResultExport/ExportResult/{operation_id}/File"
    headers = client.get_batch_header()
    headers["Accept"] = "text/plain; x-api-version=3.5"
    response = requests.get(url, headers=headers, stream=True, verify=True)
    if response.status_code == 200 and save_path:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return response


def export_and_download_calculation_results(
    client: Client,
    calculation_type: str,
    recent: bool = False,
    poll_interval: int = 5,
    timeout_minutes: int = 300,
) -> requests.Response:
    """
    Schedule a calculation result export, poll until it is ready, then download the file.
    Returns the (streamed) file download response.
    """
    response = schedule_calculation_result_export(client, calculation_type, recent=recent)
    response.raise_for_status()
    operation_id = response.json()["operationId"]

    deadline = time.time() + timeout_minutes * 60
    while time.time() < deadline:
        status_response = get_calculation_result_export_status(client, operation_id)
        status_response.raise_for_status()
        status = str(status_response.json().get("status", "")).upper()
        if status not in IN_PROGRESS_STATUSES:
            break
        time.sleep(poll_interval)
    else:
        raise TimeoutError(f"Timed out waiting for calculation result export {operation_id} to complete.")

    return download_calculation_result_export_file(client, operation_id)


if __name__ == "__main__":
    client = Client("PreProd", "stresstest-1")
    response = export_and_download_calculation_results(client, calculation_type="ESG")
    print(response.status_code)
