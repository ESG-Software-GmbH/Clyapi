import requests
from clyapi.client import Client
import clyapi


def reset_institution(client: Client) -> bool:
    key = client.config.institution_reset_key
    url = f"{client.get_active_url_prefix()}/TransactionImport/ClearAllData?key={key}"

    institution_info = clyapi.Institution.institution_info(client)["name"]
    if institution_info != "stress-testing" and "stresstest" not in institution_info:
        cli_response = input(f"Reset Institution {institution_info} on {client.institution.environment} yes/no: ")
    else:
        cli_response = "yes"

    if cli_response == "yes":
        print(f"attempting to reset institution {institution_info} on {client.institution.environment}")

        response_code = 500
        attempt = 1
        while response_code == 500:
            response = requests.post(url, headers=client.get_batch_header())
            response_code = response.status_code
            if response_code == 500:
                print(f"resetting institution failed at attempt {attempt}")
                attempt += 1

        print(f"successfully reset institution at attempt {attempt}")
        print(response.content)
        return response
    else:
        print("abortet")
        return False


if __name__ == "__main__":
    client = Client("Dev", "stress-testing")
    reset_institution(client)
    print(client)
    print(client.get_json_header())