import copy
import json
import time
# import pytest
import requests
import pandas as pd
import clyapi

import uuid

class InitialImportGenerator:
    def __init__(self, num_cp, ta_per_cp, it_per_ta, prefix = "test_initial_01_", entity_ids = None):
        self.num_cp = num_cp
        self.ta_per_cp = ta_per_cp
        self.it_per_ta = it_per_ta
        self.prefix = prefix
        self.entity_ids = entity_ids


        definitions_dir = "stress_tests/endpoint_tests/field_definitions"
        self.df_cp = pd.read_csv(f"{definitions_dir}/initial_import_cp.csv")
        self.df_ta = pd.read_csv(f"{definitions_dir}/initial_import_ta.csv")
        self.df_it = pd.read_csv(f"{definitions_dir}/initial_import_it.csv")

        self.num_rows = None        # number of cps+tas+its
        self.num_fields = None      # total number of fields to generate for comparsion with differential import

    def generate_cp_df(self, cp_ids):
        df_cp = pd.concat([self.df_cp]*len(cp_ids), ignore_index=True)
        df_cp["Counterparty_ID"] = cp_ids
        return df_cp

    def generate_ta_df(self, ta_ids, cp_ids_ta):
        df_ta = pd.concat([self.df_ta]*len(ta_ids), ignore_index=True)
        df_ta["Counterparty_ID"] = cp_ids_ta
        df_ta["Transaction_ID"] = ta_ids

        return df_ta

    def generate_it_df(self, it_ids, cp_ids_it, ta_ids_it):
        df_it = pd.concat([self.df_it]*len(it_ids), ignore_index=True)
        df_it["Counterparty_ID"] = cp_ids_it
        df_it["Transaction_ID"] = ta_ids_it
        df_it["Item_ID"] = it_ids

        return df_it

    def generate_entity_id_distribution(self):
        cps_per_entity = self.num_cp//len(self.entity_ids)
        cp_ent_ids = []
        ta_ent_ids = []
        item_ent_ids = []

        for entity_id in self.entity_ids:
            cp_ent_ids += [entity_id]*cps_per_entity
            ta_ent_ids += [entity_id]*cps_per_entity*self.ta_per_cp
            item_ent_ids +=[entity_id]*cps_per_entity*self.ta_per_cp*self.it_per_ta

        return cp_ent_ids, ta_ent_ids, item_ent_ids


    def generate_import_dfs(self):
        cp_ids = [f"{self.prefix}_{i:06d}" for i in range(self.num_cp)]
        ta_ids = [f"{self.prefix}_{i:06d}" for i in range(self.num_cp*self.ta_per_cp)]
        it_ids = [f"{self.prefix}_{i:06d}" for i in range(self.num_cp*self.ta_per_cp*self.it_per_ta)]

        cp_ids_ta = [item for item in cp_ids for _ in range(self.ta_per_cp)]
        cp_ids_it = [item for item in cp_ids for _ in range(self.ta_per_cp*self.it_per_ta)]

        ta_ids_it = [item for item in ta_ids for _ in range(self.it_per_ta)]

        df_cp = self.generate_cp_df(cp_ids)
        df_ta = self.generate_ta_df(ta_ids, cp_ids_ta)
        df_it = self.generate_it_df(it_ids, cp_ids_it, ta_ids_it)

        fixed_column_correction = 0

        if self.entity_ids != None:
            cp_ent_ids, ta_ent_ids, it_ent_ids = self.generate_entity_id_distribution()
            # Insert at position 0 (the first column)
            df_cp.insert(0, "Entity_ID", cp_ent_ids)
            df_ta.insert(0, "Entity_ID", ta_ent_ids)
            df_it.insert(0, "Entity_ID", it_ent_ids)
            fixed_column_correction = 1




        num_cp_fields = (len(df_cp.columns)-2-fixed_column_correction)*len(df_cp)
        num_ta_fields = (len(df_ta.columns)-3-fixed_column_correction)*len(df_ta)
        num_it_fields = (len(df_it.columns) - 4-fixed_column_correction)*len(df_it)

        self.num_rows = len(df_cp)+len(df_ta)+len(df_it)
        self.num_fields = num_cp_fields + num_ta_fields + num_it_fields

        return (df_cp, df_ta, df_it)

    def write_import_files(self):
        dfs = self.generate_import_dfs()

        paths = [f"stress_tests/endpoint_tests/caches/initial_import_files/{i}.csv" for i in ["cp","ta","it"]]

        for df, path in zip(dfs, paths):
            df.to_csv(path, index=False)

        return paths

    def get_request_dict(self):
        paths = self.write_import_files()

        # with open(paths[0], 'rb') as f_counterparty, \
        #         open(paths[1], 'rb') as f_transaction, \
        #         open(paths[2], 'rb') as f_item:
        f_counterparty = open(paths[0], 'rb')
        f_transaction = open(paths[1], 'rb')
        f_item = open(paths[2], 'rb')

        files = {
            "counterpartyFile": ("counterparty_file.csv", f_counterparty, "text/csv"),
            "transactionFile": ("transaction_file.csv", f_transaction, "text/csv"),
            "itemFile": ("item_file.csv", f_item, "text/csv")
        }

        return files


# class InitialImport(ApiRequest):
#     def __init__(self, cleanup=False):
#         self.operation_id = None
#         self.cleanup = cleanup
#         self.env_setup = env_setup()
#         self.prefix = "test_initial_01_"
#
#     def import_result_status(self):
#         api_prefix = self.env_setup.get("api_url")
#         url = f"{api_prefix}/api/v3.5/Import/ImportResult/{self.operation_id}"
#         response = requests.get(url, headers=self.env_setup["headers"])
#         return response.json()
#
#     def time_finish_time(self):
#         t0 = time.time()
#         status = self.import_result_status()["status"]
#         while status == "IN_PROGRESS":
#             time.sleep(0.5)
#             status = self.import_result_status()["status"]
#         return time.time() - t0
#
#     def start_initial_import(self, num_cp, ta_per_cp, it_per_ta):
#
#
#         generator = InitialImportGenerator(num_cp, ta_per_cp, it_per_ta, self.prefix)
#         files_dict = generator.get_request_dict()
#         api_url = self.env_setup.get('api_url')
#         url = f"{api_url}/api/v3.5/Import/ImportInitialFromFile"
#         headers = {
#             key: value for key, value in self.env_setup['headers'].items() if key.lower() != 'content-type'
#         }
#         response = requests.post(url, headers=headers, files=files_dict)
#         self.operation_id = response.json()["operationId"]
#         print(response.json())
#         runtime = self.time_finish_time()
#
#         fields_per_sec = generator.num_fields/runtime
#         rows_per_sec = generator.num_rows/runtime
#
#         print(f"runtime initial:{runtime} s, field write rate = {fields_per_sec} fields/s, row write rate {rows_per_sec} rows/s")
#         print(self.import_result_status())
#
#         stats_dict = {
#             "type": "initial_import",
#             "num_fields": generator.num_fields,
#             "num_rows": generator.num_rows,
#             "runtime": runtime,
#             "fields_per_sec": fields_per_sec,
#             "rows_per_sec": rows_per_sec,
#         }
#
#         return response, stats_dict


if __name__ == "__main__":
    # entity_ids = ["LE_P_VTwo", "LEC1_VTwo", "LEC2_VTwo"]
    entity_ids = ["strtst"]
    initial_generator = InitialImportGenerator(25,2,2, prefix="leo_perf_test", entity_ids=entity_ids)
    paths = initial_generator.write_import_files()
    client = clyapi.client.Client("Dev", "stress-testing")
    clyapi.endpoints.Institution.reset_institution(client)
    clyapi.endpoints.Import.initial_import(client, *paths)

    # files_dict = initial_generator.get_request_dict()
    #
    # ApiRequest().reset_institution()
    # initial_import = InitialImport()
    # initial_import.start_initial_import(1,1,4)
    # initial_import.start_initial_import(1,1,4)
