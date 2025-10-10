import os
from pathlib import Path
import json

api_statics = {
    "Dev": {
        "Url_Prefix": "https://api-burgundy.climcycle.com",
        "Resource_Id": "api://a14d8f54-c6a9-49cc-92a7-b15cace0ef36/.default",
        "Tenant": "bc476d08-a9ed-49be-8727-6c547166d422"
    },
    "PreProd": {
        "Url_Prefix": "https://api-preprod.climcycle.com",
        "Resource_Id": "api://ad585325-c053-499f-97f5-e1bb8d4fad2c/.default",
        "Tenant": "bc476d08-a9ed-49be-8727-6c547166d422"
    },
    "Prod": {
        "Url_Prefix": "https://api.climcycle.com",
        "Resource_Id": "api://cb686320-988c-4884-95d0-9dc843542f1b/.default",
        "Tenant": "1998ba70-dfcb-4c3a-bda7-a8d80d324354"
    }
}


class InstitutionConfig:
    def __init__(self, name, environment, client_application_id, client_secret):
        statics = api_statics[environment]

        self.name = name                                    # local name of the institution
        self.environment = environment                      # either Prod, Preprod, or Dev
        self.url_prefix = statics["Url_Prefix"]             # api url prefix
        self.tenant = statics["Tenant"]                     # azure Tenant uuid
        self.resource_id = statics["Resource_Id"]           # Climcycle master app registration Id
        self.client_application_id = client_application_id  # Application Id of the institution
        self.client_secret = client_secret                  # api secret of the institution

        self.auth_url = "https://login.microsoftonline.com/" + self.tenant + "/oauth2/v2.0/token"


    def __str__(self):
        prnt_str = " ".join(["Institution_Name:", self.name, "\n Environment:", self.environment, "\n Url_Prefix:", self.url_prefix, "\n Tenant_Id:", self.tenant, "\n Resources_Id:", self.resource_id, "\n Client_Application_Id:", self.client_application_id])
        return prnt_str

class ConfigManager:
    def __init__(self):
        config_dict = self.load_config_json()

        institutions = {}
        for name, config in config_dict.items():
            institution = InstitutionConfig(name, config["Environment"], config["Client_Application_Id"], config["Client_Secret"])
            institutions[name] = institution
        self.institutions = institutions
        self.active_institution = list(institutions.values())[0]

    def load_config_json(self):
        config_path = Path(os.getenv("MYAPI_CONFIG", Path.home() / ".clyapi" / "config.json"))
        try:
            with open(config_path, "r") as f:
                config_dict = json.load(f)

        except:
            dummy_instconfig = {
                "Your_Instname": {
                    "Environment": "Prod",
                    "Client_Application_Id": "some_uuid",
                    "Client_Secret": "some_uuid"
                }
                                }
            raise FileNotFoundError(f"config file has not been foung under \n{config_path} \n"
                                    f"please create the file with the following json schema: \n"
                                    f"{json.dumps(dummy_instconfig, indent=4)} \n"
                                    f"The Client_Application_Id and Client_Secret can be created in the Secret Management tab in the Climcycle tool")

        return config_dict

    def activate_instituion(self, institution_name: str):
        self.active_institution = self.institutions[institution_name]

    def __str__(self):
        str_list = []
        for institution in self.institutions.values():
            inst_str = institution.__str__()
            str_list.append(inst_str)
        prnt_str = "\n".join(str_list)
        return prnt_str


config = ConfigManager()

if __name__ == "__main__":
    config = ConfigManager()
    # print(config)
    # print(config.active_institution)
    config.activate_instituion("Quality Assurance Climcycle")