from clyapi.client import Client
from io import StringIO
import clyapi.endpoints.calculation.calculation_utils as cu
import pandas as pd

def pcr_batch(client: Client, input_filepath: str, score_preset:str = None) -> str:
    """

    Parameters
    ----------
    client: clyapi.client.Client
        clyapi client for authentification
    input_filepath: str
        Local filepath of the input .csv file. Column specification can be read from the Climcycle data requirements
    score_preset: str
        Preset of PCR scoring preset. Defaults to Climcycle Default Preset
    Returns
    -------
    csv_string: str  response file content as string
    """

    upload_response = cu.call_batch_upload_endpoint(client, input_filepath, score_preset, "PCR")
    calculation_id = upload_response["data"]["calculationResultId"]  #get calculation id from response

    result_file_info =cu.get_result_files_info(client, calculation_id, wait_seconds=1)
    file_id = result_file_info["resultFiles"][0]["id"]

    response_content = cu.get_result_file_csv(client, file_id)
    csv_content = response_content.content.decode("utf-8")

    return csv_content

def pcr_batch_to_file(client: Client, input_filepath: str, output_filepath, score_preset:str = None) -> None:
    csv_content = pcr_batch(client, input_filepath)
    # Write to a CSV file
    with open(output_filepath, "w", encoding="utf-8", newline="") as f:
        f.write(csv_content)
    print(f"saved pcr portfolio as csv file to {output_filepath}")
    return

def pcr_batch_to_dataframe(client: Client, input_filepath: str, score_preset:str = None) -> pd.DataFrame:
    csv_content = pcr_batch(client, input_filepath)
    csv_buffer = StringIO(csv_content)
    df = pd.read_csv(csv_buffer)
    return df.iloc[:,1:]   # drop first column, which for some reason get added by the endpoint


if __name__ == "__main__":
    import numpy as np
    import pandas as pd

    num = 10
    test_dict = {
        "Counterparty_ID": np.arange(0,num).astype(str),
        "Transaction_ID": np.arange(0,num).astype(str),
        "Item_ID": np.arange(0,num).astype(str),
        "Item_Longitude": np.linspace(10,15,num),
        "Item_Latitude": np.linspace(40,45, num),
        "Item_Origination_Date": "2025-01-01",
        "Item_Maturity_Date": "2055-01-01",
        "GCA": 100.0,
        "GCA_Share": 1.0,
        "Item_Nace_Code": "D 35.11"
    }
    file_path = "/Users/leonardmueller/Documents/git/Clyapi/data/batch_example_portfolios/pcr_input.csv"


    client = Client("Stark Bank")
    print(client)

    pcr_batch(client, file_path)
    pcr_batch_to_file(client, file_path, "test_pcr_out")

    df = pcr_batch_to_dataframe(client, file_path)
    print(df)