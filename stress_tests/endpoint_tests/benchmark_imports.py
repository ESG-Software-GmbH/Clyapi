from call_initial_import import InitialImport
from call_differential_import import DifferntialImport, ApiRequest
import csv
import os
from azure_scaler import scale_elastic_pool
import math
import time

def append_dict_to_csv(file_path, row_dict):
    file_exists = os.path.exists(file_path)

    with open(file_path, 'a+', newline='') as csvfile:
        csvfile.seek(0)
        is_empty = csvfile.read(1) == ''
        csvfile.seek(0, os.SEEK_END)  # Move pointer back to end for writing

        writer = csv.DictWriter(csvfile, fieldnames=row_dict.keys())

        # If file is new or empty, write header
        if not file_exists or is_empty:
            writer.writeheader()

        # Write the dictionary as a new row
        writer.writerow(row_dict)

def increasing_initial_calls(num_cps_list: list, ratio = 4):
    init_import = InitialImport()
    for num_cps in num_cps_list:
        prefix = f"bm_init_0_{num_cps:03d}_"
        init_import.prefix = prefix
        response, stats_dict = init_import.start_initial_import(num_cps, ratio, ratio)
        append_dict_to_csv("caches/stats/comparison.csv", stats_dict)

def increasing_differential_call(num_cps_list: list, ratio = 4):
    diff_import = DifferntialImport()
    for num_cps in num_cps_list:
        prefix = f"bm_diff_0_{num_cps:03d}_"
        diff_import.prefix = prefix
        response, stats_dict = diff_import.start_differential_import(num_cps, ratio, ratio)
        append_dict_to_csv("caches/stats/diff_import_paused.csv", stats_dict)


def increasing_dtus_comparison(ratio = 4):
    diff_import = DifferntialImport()
    init_import = InitialImport()
    for j in [4]:
        ApiRequest().reset_institution()
        num_cps = j*20
        diff_import.prefix = f"bm_init_0_{num_cps:03d}_"
        init_import.prefix = f"bm_diff_0_{num_cps:03d}_"
        # scale_elastic_pool(j*100)
        response, stats_dict = diff_import.start_differential_import(int(math.sqrt(j)*30), ratio, ratio)
        append_dict_to_csv("caches/stats/comparison_serverless.csv", stats_dict)
        response, stats_dict = init_import.start_initial_import(num_cps, ratio, ratio)
        append_dict_to_csv("caches/stats/comparison_serverless.csv", stats_dict)

    # scale_elastic_pool(1 * 100)

def consecutive_imports(ratio=4):
    init_import = InitialImport()
    for i in [1,2,3,4,5,6]:
        init_import.prefix=f"consecutive_{i}_"
        num_cps = 1000
        response, stats_dict = init_import.start_initial_import(num_cps, ratio, ratio)
        append_dict_to_csv("caches/stats/import_paused_calcs.csv", stats_dict)
        print("sleeping 5 minutes for calculations to finish")
        time.sleep(300)


if __name__ == "__main__":
    # ApiRequest().reset_institution()
    # num_cps_list = [1,2,4,8,16,32,64,128,2**8,2**9,2**10]
    # num_cps_list = num_cps_list[-1:]
    # num_cps_list = [19000]
    increasing_differential_call([100,100,100])
    # increasing_initial_calls(num_cps_list)
    # increasing_dtus_comparison()
    # consecutive_imports()


    # around 380 fields /s was average initial import writespeed on dev database, with 100 dtus
    # around 200 fields /s was average differential import writespeed on dev database, with 100 dtus
    # around 500 fields /s was average initial import writespeed on dev database, with 200 dtus
    # around 300 fields /s was average differential import writespeed on dev database, with 200 dtus
    pass