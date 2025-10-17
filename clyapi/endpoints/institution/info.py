import requests
from clyapi.client import Client

def institution_info(client: Client)-> dict:
    url = f"{client.institution.url_prefix}/api/v3.5/Institution/InstitutionInfo"
    response = requests.get(url, headers=client.get_json_header()).json()
    return response

if __name__ == "__main__":
    client = Client()
    print(type(institution_info(client)))