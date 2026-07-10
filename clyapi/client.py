import requests
from clyapi.api_config import ConfigManager, InstitutionConfig


class Client:
    """
    The Client handles the basic api functionality like authorization and credential management. It expects a
    configuration file under ~/.clyapi/config.json with settings for institutions.
    """

    def __init__(self, environment: str, institution_name: str | None = None):
        # If a profile is explicitly given, activate it
        self.config = ConfigManager()
        if institution_name:
            self.config.activate_institution(environment, institution_name)
        # Read the currently active configuration
        self.institution: InstitutionConfig = self.config.active_institution


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

    def get_json_header(self):
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            "Content-Type": "application/json-patch+json; x-api-version=3.5"
        }
        return headers


    def get_batch_header(self):
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
        }
        return headers

    def get_active_url_prefix(self):
        return self.institution.url_prefix

    def get_legacy_env_setup(self, entity_id=None):
        return {
            "api_url": self.institution.url_prefix,
            "headers": None,
            "token": self.get_access_token(),
            "institution_type": self.institution.type,
            "entity_type": entity_id,
        }

    def __str__(self):
        return f"Active Institution:\n {self.institution}"

if __name__ == "__main__":

    pass