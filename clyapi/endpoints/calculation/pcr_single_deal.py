from clyapi.client import Client
import requests


def physical_climate_risks_single(client: Client, Item_Longitude: float, Item_Latitude: float, Item_Origination_Date: str,
                                  Item_Maturity_Date: str, Item_Nace_Code: str, Counterparty_Id: str = "clyapi_dummy", Transaction_Id: str = "clyapi_dummy",
                                  Item_Id: str = "clyapi_dummy", Score_Preset_Code: str = None, Item_Radius = None, Item_Center_Weight = None, Maximum_Assessment = False) -> dict:
    """

    Parameters
    ----------
    client: clyapi.clyapi.Client
        clyapi client for authentification
    Item_Longitude: float
        Coordinate Longitude to be analyzed
    Item_Latitude:
        Corrdinate Latitude to be analyzed
    Item_Origination_Date: str
        Origination date in the format "YYYY-MM-DD"
    Item_Maturity_Date: str
        Maturity date in the format "YYYY-MM-DD"
    Item_Nace_Code: str
        Nace code of the Item, check documentation for valid nace codes
    Counterparty_Id: str
        Optional counterparty identifier
    Transaction_Id: str
        Optional transaction identifier
    Item_Id: str
        Optional item identifier
    Score_Preset_Code: str
        Optional code of the scoring preset found in the tool, defaults to the Climcycle default preset
    Item_Radius: float
        Optional radius [km] to be included in the calculation.
    Item_Center_Weight: float
        Optional weight of the center point to compared to the rest of the radius [1]
    Maximum_Assessment: bool
        Optional set to get the maximum risk score in the radius, will overwrite the Item_Center_Weight option

    Returns
    -------
    dict
        nested dictionary of PCR risks and associated values.
    """

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
    }
    if Item_Radius != None:
        payload["Item_Radius"] = Item_Radius
        payload["Item_Center_Weight"] = Item_Center_Weight
        payload["Maximum_Assessment"] = Maximum_Assessment


    response = requests.post(url, headers=client.headers, json=payload)
    assert response.status_code == 200
    return response.json()
