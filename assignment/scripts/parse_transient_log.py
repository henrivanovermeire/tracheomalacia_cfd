#!/usr/bin/env python3
"""Stream a pimpleFoam log into compact convergence data and summary statistics."""

import argparse
import csv
import json
import math
import re
from pathlib import Path

COURANT = re.compile(r"Courant Number mean:\s*([0-9.eE+-]+)\s+max:\s*([0-9.eE+-]+)")
DELTA_T = re.compile(r"deltaT =\s*([0-9.eE+-]+)")
TIME = re.compile(r"Time =\s*([0-9.eE+-]+)")
EXECUTION = re.compile(r"ExecutionTime =\s*([0-9.eE+-]+)\s+s\s+ClockTime =\s*([0-9.eE+-]+)\s+s")
CONTINUITY = re.compile(
    r"time step continuity errors\s*:\s*sum local =\s*([0-9.eE+-]+),\s*"
    r"global =\s*([0-9.eE+-]+),\s*cumulative =\s*([0-9.eE+-]+)"
)
CONVERGED = re.compile(r"PIMPLE: converged in\s+(\d+)\s+iterations")
NOT_CONVERGED = re.compile(r"PIMPLE: not converged within\s+(\d+)\s+iterations")


def finite(value):
    return value is not None and math.isfinite(value)


def parse(path):
    pending = {"courant_mean": None, "courant_max": None, "delta_t_s": None}
    current = None
    rows = []
    with path.open("r", errors="replace") as source:
        for line in source:
            match = COURANT.search(line)
            if match:
                pending["courant_mean"] = float(match.group(1))
                pending["courant_max"] = float(match.group(2))
                continue
            match = DELTA_T.search(line)
            if match:
                pending["delta_t_s"] = float(match.group(1))
                continue
            match = TIME.match(line.strip())
            if match:
                value = float(match.group(1))
                if value <= 0 or value > 2.000001:
                    continue
                current = {
                    "time_s": value,
                    **pending,
                    "pimple_converged": None,
                    "pimple_iterations": None,
                    "continuity_local": None,
                    "continuity_global": None,
                    "continuity_cumulative": None,
                    "execution_time_s": None,
                    "clock_time_s": None,
                }
                rows.append(current)
                continue
            if current is None:
                continue
            match = CONTINUITY.search(line)
            if match:
                current["continuity_local"] = float(match.group(1))
                current["continuity_global"] = float(match.group(2))
                current["continuity_cumulative"] = float(match.group(3))
                continue
            match = CONVERGED.search(line)
            if match:
                current["pimple_converged"] = True
                current["pimple_iterations"] = int(match.group(1))
                continue
            match = NOT_CONVERGED.search(line)
            if match:
                current["pimple_converged"] = False
                current["pimple_iterations"] = int(match.group(1))
                continue
            match = EXECUTION.search(line)
            if match:
                current["execution_time_s"] = float(match.group(1))
                current["clock_time_s"] = float(match.group(2))
    return [row for row in rows if row["pimple_converged"] is not None]


def sample_rows(rows, maximum):
    if len(rows) <= maximum:
        return rows
    stride = math.ceil(len(rows) / maximum)
    selected = rows[::stride]
    for row in rows:
        if not row["pimple_converged"]:
            selected.append(row)
    selected.append(rows[-1])
    return sorted({row["time_s"]: row for row in selected}.values(), key=lambda row: row["time_s"])


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--csv", type=Path, default=Path("assignment/data/postop_transient_coarse_poc_convergence.csv"))
    parser.add_argument("--summary", type=Path, default=Path("assignment/data/postop_transient_coarse_poc_convergence.json"))
    parser.add_argument("--maximum-csv-rows", type=int, default=5000)
    args = parser.parse_args()
    rows = parse(args.log)
    if not rows:
        raise SystemExit(f"No completed PIMPLE timesteps found in {args.log}")
    sampled = sample_rows(rows, args.maximum_csv_rows)
    write_csv(sampled, args.csv)
    failed = [row for row in rows if not row["pimple_converged"]]
    max_co = max(row["courant_max"] for row in rows if finite(row["courant_max"]))
    max_mean_co = max(row["courant_mean"] for row in rows if finite(row["courant_mean"]))
    min_dt = min(row["delta_t_s"] for row in rows if finite(row["delta_t_s"]))
    max_dt = max(row["delta_t_s"] for row in rows if finite(row["delta_t_s"]))
    cumulative = [abs(row["continuity_cumulative"]) for row in rows if finite(row["continuity_cumulative"])]
    summary = {
        "schema_version": 1,
        "log": str(args.log),
        "completed_timesteps": len(rows),
        "converged_timesteps": len(rows) - len(failed),
        "not_converged_timesteps": len(failed),
        "converged_fraction_percent": 100.0 * (len(rows) - len(failed)) / len(rows),
        "first_not_converged_time_s": failed[0]["time_s"] if failed else None,
        "last_not_converged_time_s": failed[-1]["time_s"] if failed else None,
        "maximum_courant_number": max_co,
        "maximum_mean_courant_number": max_mean_co,
        "minimum_delta_t_s": min_dt,
        "maximum_delta_t_s": max_dt,
        "maximum_absolute_cumulative_continuity_error": max(cumulative) if cumulative else None,
        "final_execution_time_s": rows[-1]["execution_time_s"],
        "final_clock_time_s": rows[-1]["clock_time_s"],
        "final_time_s": rows[-1]["time_s"],
        "csv_rows": len(sampled),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"CSV: {args.csv}")
    print(f"Summary: {args.summary}")


if __name__ == "__main__":
    main()
