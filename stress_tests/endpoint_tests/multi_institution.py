import csv
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import clyapi
from call_initial_import import InitialImportGenerator

stress_institutions = ["stresstest-1", "stresstest-2", "stresstest-3", "stresstest-4", "stresstest-5", "stresstest-6",
                "stresstest-7", "stresstest-8", "stresstest-9", "stresstest-10"]

LOG_DIR = Path("stress_tests/endpoint_tests/caches/multi_institution_logs")

# Core columns always present in the metrics CSV; operation-specific metric keys are appended after these.
METRICS_CORE_COLUMNS = ["timestamp", "run_name", "operation", "institution", "status", "duration_s"]


def build_client_dict(institutions, environment="PreProd"):
    client_dict = {}
    for institution in institutions:
        client = clyapi.client.Client(environment, institution)
        client_dict[institution] = client
    return client_dict


class MetricsLog:
    """
    Buffers one structured record per (institution x operation) and writes them as a
    CSV so runtimes, file sizes, row counts etc. can be pulled with pandas/Excel.
    The column set is the union of all record keys, core columns first.
    """

    def __init__(self, csv_path, run_name):
        self.csv_path = csv_path
        self.run_name = run_name
        self.rows = []

    def add(self, row):
        self.rows.append(row)
        self.flush()  # flush after every record so partial runs are still analysable

    def flush(self):
        extra_columns = []
        for row in self.rows:
            for key in row:
                if key not in METRICS_CORE_COLUMNS and key not in extra_columns:
                    extra_columns.append(key)
        fieldnames = METRICS_CORE_COLUMNS + extra_columns

        with open(self.csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)


def setup_logging(run_name):
    """
    Create timestamped output files under LOG_DIR:
      - <run_name>_<ts>.log  human-readable progress log
      - <run_name>_<ts>.csv  structured metrics (one row per institution x operation)
    Returns (logger, metrics_log).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{run_name}_{timestamp}"
    log_path = LOG_DIR / f"{stem}.log"
    csv_path = LOG_DIR / f"{stem}.csv"

    logger = logging.getLogger(f"multi_institution.{stem}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    for handler in (logging.FileHandler(log_path), logging.StreamHandler()):
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info(f"log file: {log_path}")
    logger.info(f"metrics csv: {csv_path}")
    return logger, MetricsLog(csv_path, run_name)


class MultiInstitutionRunner:
    """
    Runs API operations across many institutions in parallel and records the duration
    and input parameters of every operation on a per-institution basis.
    """

    def __init__(self, client_dict, logger, metrics_log, max_workers=None):
        self.client_dict = client_dict
        self.logger = logger
        self.metrics_log = metrics_log
        self.max_workers = max_workers or len(client_dict)

    def run_operation(self, operation_name, operation_fn, metrics=None, **params):
        """
        Execute operation_fn(client, **params) for every institution in parallel.

        operation_name: label used in the log lines and CSV.
        operation_fn:   callable taking (client, **params).
        metrics:        dict of structured numbers (file sizes, row counts, ...) attached
                        as extra columns to every institution's CSV row.
        params:         keyword args forwarded to operation_fn; logged verbatim in the text log.

        Returns {institution_name: {"status", "duration", "result"|"error"}}.
        """
        metrics = metrics or {}
        self.logger.info(f"START operation '{operation_name}' on {len(self.client_dict)} institutions | params={params} | metrics={metrics}")
        results = {}

        def _task(name, client):
            t0 = time.time()
            self.logger.info(f"[{name}] START '{operation_name}' | params={params}")
            try:
                result = operation_fn(client, **params)
                duration = time.time() - t0
                self.logger.info(f"[{name}] DONE '{operation_name}' | duration={duration:.2f}s")
                return name, "ok", duration, result, None
            except Exception as exc:
                duration = time.time() - t0
                self.logger.exception(f"[{name}] FAILED '{operation_name}' | duration={duration:.2f}s | error={exc}")
                return name, "error", duration, None, str(exc)

        run_t0 = time.time()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(_task, name, client) for name, client in self.client_dict.items()]
            for future in as_completed(futures):
                name, status, duration, result, error = future.result()
                results[name] = {"status": status, "duration": duration, "result": result, "error": error}
                self.metrics_log.add({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "run_name": self.metrics_log.run_name,
                    "operation": operation_name,
                    "institution": name,
                    "status": status,
                    "duration_s": round(duration, 3),
                    **metrics,
                })

        total = time.time() - run_t0
        ok = sum(1 for r in results.values() if r["status"] == "ok")
        self.logger.info(f"FINISH operation '{operation_name}' | total_wall_time={total:.2f}s | ok={ok}/{len(results)}")
        return results


# ------------------------------
''' Operation wrappers: each takes (client, **params) so they plug into run_operation. '''
# ------------------------------

def op_reset(client):
    return clyapi.endpoints.Institution.reset_institution(client)


def op_initial_import(client, counterpartyFile, transactionFile, itemFile):
    return clyapi.endpoints.Import.initial_import(client, counterpartyFile, transactionFile, itemFile)

def op_full_export(client):
    return clyapi.endpoints.Export.export_and_download_complete(client)


# ------------------------------
''' Example stress run: reset every institution, then import the same files into all of them in parallel. '''
# ------------------------------

def import_stress(client_dict, num_cp=2, ta_per_cp=2, it_per_ta=2):
    logger, metrics_log = setup_logging("import_stress")
    runner = MultiInstitutionRunner(client_dict, logger, metrics_log)

    generator = InitialImportGenerator(num_cp, ta_per_cp, it_per_ta, prefix="leo_perf_test")
    paths = generator.write_import_files()
    cp_path, ta_path, it_path = paths

    # Per-file row counts (data rows, excluding the header) and byte sizes for later metric calculations.
    file_metrics = {}
    total_rows = 0
    for label, path in zip(["cp", "ta", "it"], paths):
        with open(path) as f:
            rows = sum(1 for _ in f) - 1  # subtract header
        size = Path(path).stat().st_size
        file_metrics[f"rows_{label}"] = rows
        file_metrics[f"bytes_{label}"] = size
        total_rows += rows
    file_metrics["total_rows"] = total_rows
    file_metrics["total_bytes"] = sum(file_metrics[f"bytes_{l}"] for l in ["cp", "ta", "it"])
    file_metrics.update({"num_cp": num_cp, "ta_per_cp": ta_per_cp, "it_per_ta": it_per_ta})

    logger.info(f"generated import files: {paths}")
    logger.info(f"import file metrics: {file_metrics}")

    runner.run_operation("reset_institution", op_reset)
    runner.run_operation(
        "initial_import",
        op_initial_import,
        metrics=file_metrics,
        counterpartyFile=cp_path,
        transactionFile=ta_path,
        itemFile=it_path,
    )


if __name__ == "__main__":
    client_dict = build_client_dict(stress_institutions)
    import_stress(client_dict, num_cp=25000)
