import requests
from clyapi.api_config import config, InstitutionConfig


class Client:
    def __init__(self, profile: str | None = None):
        # If a profile is explicitly given, activate it
        if profile:
            config.activate_instituion(profile)
        # Read the currently active configuration
        self.institution: InstitutionConfig = config.active_institution
        self.headers = self.build_header()


    def get_access_token(self):
        institution = self.institution

        token_url = institution.auth_url
        payload = {
            'grant_type': 'client_credentials',
            'client_id': institution.client_application_id,
            'client_secret': institution.client_secret,
            'scope': institution.resource_id
        }
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json().get('access_token')

    def build_header(self):
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            "Content-Type": "application/json-patch+json; x-api-version=3.5"
        }
        return headers


    def __str__(self):
        return f"Active Institution:\n {self.institution}"

if __name__ == "__main__":
    client = Client()
    token = client.get_access_token()
    print(client.get_institution_info())
    # print(token)