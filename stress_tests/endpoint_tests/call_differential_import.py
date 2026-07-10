import copy
import json
import time
from pkgutil import ImpImporter
import pandas as pd

import pytest
import requests
from generate_env_setup import env_setup, get_institution_info
import uuid
import csv
from itertools import islice


class ImportLayout:
    def __init__(self, num_cp, ta_per_cp, it_per_ta, prefix):
        self.num_cp = num_cp
        self.ta_per_cp = ta_per_cp
        self.it_per_ta = it_per_ta
        self.prefix = prefix
        self.num_rows = num_cp*ta_per_cp*it_per_ta
        self.num_fields = 0

    def read_fields(self, csv_path):
        with open(csv_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
        data = data[0]
        id_fields = ["Branch_ID","Counterparty_ID","Transaction_ID","Item_ID"]
        data = {key: value for key, value in data.items() if key not in id_fields}
        # data = dict(islice(data.items(), 20))
        return data

    def generate_counterparties(self):
        request_list = []
        field_dict = self.read_fields("stress_tests/endpoint_tests/field_definitions/initial_import_cp.csv")
        for i in range(self.num_cp):
            j = 0
            for fieldcode, value in field_dict.items():
                if j == 0:
                    action = "Create"
                else:
                    action = "Update"
                listitem = {
                    "action": action,
                    "branchId": "",
                    "counterpartyId": f"{self.prefix}{i}",
                    "transactionId": "",
                    "itemId": "" ,
                    "fieldCode": fieldcode,
                    "value": value
                }
                request_list.append(listitem)
                j+=1
        self.num_fields += len(request_list)
        return request_list

    def generate_transactions(self, counter_parties):
        request_list = []
        field_dict = self.read_fields("stress_tests/endpoint_tests/field_definitions/initial_import_ta.csv")
        for i in range(self.num_cp):
            for _ in range(self.ta_per_cp):
                j = 0
                for fieldcode, value in field_dict.items():
                    if j == 0:
                        action = "Create"
                    else:
                        action = "Update"

                    listitem = {
                        "action": action,
                        "branchId": "",
                        "counterpartyId": f"{self.prefix}{i}",
                        "transactionId": f"{self.prefix}{i}_{_}",
                        "itemId": "" ,
                        "fieldCode": fieldcode,
                        "value": value
                    }
                    request_list.append(listitem)
                    j+=1

        self.num_fields += len(request_list)
        return request_list

    def generate_items(self, counterparties, transactions):
        request_list = []
        field_dict = self.read_fields("stress_tests/endpoint_tests/field_definitions/initial_import_it.csv")
        unique_transactions = [value["transactionId"] for value in transactions]
        unique_transactions = list(set(unique_transactions))
        for j , transaction_id in enumerate(unique_transactions):
            # print(j)
            for _ in range(self.it_per_ta):
                j = 0
                for fieldcode, value in field_dict.items():
                    if j == 0:
                        action = "Create"
                    else:
                        action = "Update"

                    listitem = {
                        "action": action,
                        "branchId": "",
                        "counterpartyId": "_".join(transaction_id.split("_")[:-1]),
                        "transactionId": transaction_id,
                        "itemId": f"{self.prefix}{_}",
                        "fieldCode": fieldcode,
                        "value": value
                    }
                    request_list.append(listitem)
                    j+=1

        self.num_fields += len(request_list)
        return request_list


    def generate_deletes(self, create_queries):
        request_list = []
        del_queries = copy.deepcopy(create_queries)
        for request in del_queries:
            request["action"] = "Delete"
            request_list.append(request)
        # reverse list because items must be deleted before transactions and counterparties
        request_list = request_list[::-1]
        return request_list


    def generate_query(self, delete=True):
        """
        Creates a query to import data into the system.

            list: A list of queries, where each query is a dictionary representing
                an insert or delete operation.
        """
        counterparties = self.generate_counterparties()
        transactions = self.generate_transactions(counterparties)
        items = self.generate_items(counterparties, transactions)
        create_queries = counterparties+transactions+items
        delete_rows = self.generate_deletes(create_queries)

        if delete:
            return create_queries, delete_rows
        else:
            num_items = self.num_cp + self.ta_per_cp + self.it_per_ta
            # assert num_items < 10, "not allowed to create more than 10 entries without deleting"
            return create_queries, []


class ApiRequest:
    def __init__(self):
        self.env_setup = env_setup()

    def reset_institution(self):
        prefix = self.env_setup["api_url"]
        url = f"{prefix}/api/TransactionImport/ClearAllData?key="
        header = {}
        header["Authorization"] = self.env_setup['headers']["Authorization"]

        institution_info = get_institution_info(self.env_setup)["name"]
        if institution_info != "stress-testing":
            cli_response = input(f"Reset Institution {institution_info} on {prefix} yes/no: ")
        else:
            cli_response = "yes"


        if cli_response == "yes":
            print(f"attempting to reset institution {institution_info}")

            response_code = 500
            attempt = 1
            while response_code == 500:
                response = requests.post(url, headers=header)
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

class DifferntialImport(ApiRequest):
    def __init__(self, cleanup=True):
        self.operation_id = None
        self.cleanup = cleanup
        self.prefix = "stress_test_1_0"
        self.env_setup = env_setup()

    def get_counterparties(self, import_list):
        counterparties = [entry["counterpartyId"] for entry in import_list]
        counterparties = set(counterparties)
        return counterparties

    def get_transactions(self, import_list):
        transactions = [entry["transactionId"] for entry in import_list]
        transactions = set(transactions)
        return transactions


    def delete_counterparties(self, counterparties, transactions):
        prefix = self.env_setup["api_url"]
        responses = []
        for tr in transactions:
            url = f"{prefix}/api/v3.5/Transaction/{tr}/"
            response = requests.delete(url=url, headers=self.env_setup['headers'])
            responses.append(response)

        for cp in counterparties:
            url = f"{prefix}/api/v3.5/Counterparty/{cp}/"
            response = requests.delete(url=url, headers=self.env_setup['headers'])
            responses.append(response)

        return responses

    def start_differential_import(self, num_cp, ta_per_cp, it_per_ta):
        # print(self.env_setup)
        url_prefix = self.env_setup.get('api_url')
        # print(get_institution_info(self.env_setup))
        institution_info = get_institution_info(self.env_setup)["name"]



        import_layout = ImportLayout(num_cp, ta_per_cp, it_per_ta, self.prefix)
        import_list, delete_list = import_layout.generate_query(delete=self.cleanup)
        # print(f"starting differential import for institution {institution_info} on environment {url_prefix} with {len(import_list)} number of fields")
        import_data = json.dumps(import_list)
        url = f"{url_prefix}/api/v3.5/Import/ImportDifferential"
        create_response = requests.post(url, headers=self.env_setup['headers'], data=import_data)
        assert create_response.status_code == 200
        self.operation_id = create_response.json()["operationId"]
        runtime = self.time_finish_time()
        status = self.import_result_status()
        fields_per_sec = import_layout.num_fields/runtime
        rows_per_sec = import_layout.num_rows/runtime

        print(f"runtime differential: {runtime} field write rate = {fields_per_sec} fields/s, row write rate {rows_per_sec} rows/s")
        # responses = self.delete_counterparties(counterparties, transactions)
        # print(responses)

        stats_dict = {
            "type": "differential_import",
            "num_fields": import_layout.num_fields,
            "num_rows": import_layout.num_rows,
            "runtime": runtime,
            "fields_per_sec": fields_per_sec,
            "rows_per_sec": rows_per_sec,
        }


        return create_response.json(), stats_dict

    def import_result_status(self):
        api_prefix = self.env_setup.get("api_url")
        url = f"{api_prefix}/api/v3.5/Import/ImportResult/{self.operation_id}"
        response = requests.get(url, headers=self.env_setup["headers"])
        return response.json()

    def time_finish_time(self):
        t0 = time.time()
        status = self.import_result_status()["status"]
        while status == "IN_PROGRESS":
            time.sleep(0.5)
            status = self.import_result_status()["status"]
        return time.time()-t0

if __name__ == "__main__":
    # diff_import = DifferntialImport(cleanup = True)
    # diff_import.reset_institution()
    # ApiRequest().reset_institution()
    number = 1000
    # operation_ID = diff_import.start_differential_import(number,1,1)
    layout = ImportLayout(number, 1,1, "bench_diff")
    query = layout.generate_query(delete=False)
    df = pd.DataFrame(query[0])
    df = df.rename(columns ={"action":"Action", "branchId": "Branch_ID", "counterpartyId": "Counterparty_ID", "transactionId": "Transaction_ID", "itemId": "Item_ID", "fieldCode": "FieldCode", "value": "Value"})
    print(df)
    df.to_csv("stress_tests/endpoint_tests/caches/diff_import.csv")
    # time.sleep(0.3)
    # runtime = diff_import.time_finish_time()
    # status = diff_import.import_result_status()
    # print(f"runtime: {runtime} \n status: {status}")
