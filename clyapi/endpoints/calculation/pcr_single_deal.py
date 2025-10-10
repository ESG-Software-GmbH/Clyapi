from clyapi.client import Client
import requests


def physical_climate_risks_single(client: Client, Item_Longitude: float, Item_Latitude: float, Item_Origination_Date: str,
                                  Item_Maturity_Date: str, Item_Nace_Code: str, Counterparty_Id: str = "dummy", Transaction_Id: str = "dummy",
                                  Item_Id: str = "dummy", Score_Preset_Code: str = None, Item_Radius = None) -> dict:

    url = f"{client.institution.url_prefix}/api/v3.5/Calculation/CalculateSinglePhysicalRisks"
    payload = {
        "Score_Preset_Code": Score_Preset_Code,
        "Counterparty_ID": Counterparty_Id,
        "Transaction_ID": Transaction_Id,
        "Item_ID": Item_Id,
        "Item_Longitude": Item_Longitude,
        "Item_Latitude": Item_Latitude,
        "Item_Origination_Date": Item_Origination_Date,
        "Item_Maturity_Date": Item_Maturity_Date,
        "Item_NACE_Code": Item_Nace_Code,
        "Item_Radius": Item_Radius
    }
    response = requests.post(url, headers=client.headers, json=payload)
    assert response.status_code == 200
    return response.json()
