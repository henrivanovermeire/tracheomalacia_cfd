#!/usr/bin/env python3
"""Extract simpleFoam residuals and create a convergence figure."""

import argparse
import csv
import re
import subprocess
from pathlib import Path

TIME_RE = re.compile(r"^Time = (\d+)$")
SOLVE_RE = re.compile(
    r"Solving for (Ux|Uy|Uz|p), Initial residual = ([0-9.eE+-]+), "
    r"Final residual = ([0-9.eE+-]+), No Iterations (\d+)"
)
CONTINUITY_RE = re.compile(
    r"time step continuity errors : sum local = ([0-9.eE+-]+), "
    r"global = ([0-9.eE+-]+), cumulative = ([0-9.eE+-]+)"
)


def parse_log(path):
    rows = []
    current = None
    pressure_solves = []

    def finish_iteration():
        nonlocal current, pressure_solves
        if current is None:
            return
        if pressure_solves:
            current["p_initial"] = pressure_solves[0][0]
            current["p_final"] = pressure_solves[-1][1]
            current["p_corrections"] = len(pressure_solves)
        required = {"iteration", "Ux_initial", "Uy_initial", "Uz_initial", "p_initial"}
        if required.issubset(current):
            rows.append(current)
        current = None
        pressure_solves = []

    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.strip()
        time_match = TIME_RE.match(line)
        if time_match:
            finish_iteration()
            current = {"iteration": int(time_match.group(1))}
            continue
        if current is None:
            continue
        solve_match = SOLVE_RE.search(line)
        if solve_match:
            field = solve_match.group(1)
            initial = float(solve_match.group(2))
            final = float(solve_match.group(3))
            linear_iterations = int(solve_match.group(4))
            if field == "p":
                pressure_solves.append((initial, final, linear_iterations))
            else:
                current[f"{field}_initial"] = initial
                current[f"{field}_final"] = final
                current[f"{field}_linear_iterations"] = linear_iterations
            continue
        continuity_match = CONTINUITY_RE.search(line)
        if continuity_match:
            current["continuity_local"] = float(continuity_match.group(1))
            current["continuity_global"] = float(continuity_match.group(2))
            current["continuity_cumulative"] = float(continuity_match.group(3))
    finish_iteration()
    return rows


def write_csv(rows, path):
    fields = [
        "iteration", "Ux_initial", "Uy_initial", "Uz_initial", "p_initial",
        "Ux_final", "Uy_final", "Uz_final", "p_final", "p_corrections",
        "Ux_linear_iterations", "Uy_linear_iterations", "Uz_linear_iterations",
        "continuity_local", "continuity_global", "continuity_cumulative",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def plot(csv_path, tex_path):
    """Generate a LaTeX/PDF residual plot through Gnuplot cairolatex."""
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    plot_script = tex_path.resolve().with_suffix(".gp")
    csv_absolute = csv_path.resolve().as_posix()
    report_directory = tex_path.resolve().parents[1]
    output_path = tex_path.resolve().relative_to(report_directory).as_posix()
    script = f'''set terminal cairolatex pdf color size 15cm,9cm font ",10"
set output "{output_path}"
set datafile separator comma
set key outside top center horizontal maxrows 2
set grid xtics ytics mxtics mytics back lc rgb "#d0d0d0"
set logscale y
set format y "$10^{{%T}}$"
set xlabel "SIMPLE iteration"
set ylabel "Initial residual"
set xrange [1:*]
set yrange [1e-7:1]
set title "Postoperative steady-solver convergence"
plot "{csv_absolute}" using 1:2 every ::1 with lines lw 1.5 title "$U_x$", \\
     "{csv_absolute}" using 1:3 every ::1 with lines lw 1.5 title "$U_y$", \\
     "{csv_absolute}" using 1:4 every ::1 with lines lw 1.5 title "$U_z$", \\
     "{csv_absolute}" using 1:5 every ::1 with lines lw 1.5 title "$p$", \\
     1e-6 with lines dt 2 lw 1.2 lc rgb "black" title "$U$ criterion", \\
     1e-5 with lines dt 3 lw 1.2 lc rgb "#666666" title "$p$ criterion"
unset output
'''
    plot_script.write_text(script)
    subprocess.run(
        ["gnuplot", str(plot_script)], check=True, cwd=report_directory
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "log", nargs="?",
        default="results/postop_assignment4/log.simpleFoam.parallel",
        type=Path,
    )
    parser.add_argument(
        "--csv", default="assignment/data/postop_assignment4_residuals.csv", type=Path
    )
    parser.add_argument(
        "--figure", default="report/figures/assignment4_residuals.tex", type=Path
    )
    args = parser.parse_args()
    rows = parse_log(args.log)
    if not rows:
        raise SystemExit(f"No complete SIMPLE iterations parsed from {args.log}")
    write_csv(rows, args.csv)
    plot(args.csv, args.figure)
    final = rows[-1]
    print(f"Parsed {len(rows)} iterations; final iteration: {final['iteration']}")
    print(
        "Final initial residuals: "
        f"Ux={final['Ux_initial']:.6g}, Uy={final['Uy_initial']:.6g}, "
        f"Uz={final['Uz_initial']:.6g}, p={final['p_initial']:.6g}"
    )
    print(f"CSV: {args.csv}")
    print(f"Figure: {args.figure}")


if __name__ == "__main__":
    main()
