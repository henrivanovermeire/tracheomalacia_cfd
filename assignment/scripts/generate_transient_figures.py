#!/usr/bin/env python3
"""Generate Assignment 6 convergence and cycle-response figures with Gnuplot."""

import argparse
import subprocess
from pathlib import Path


def run_gnuplot(script_path, working_directory):
    subprocess.run(["gnuplot", str(script_path.resolve())], cwd=working_directory, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--convergence", type=Path, default=Path("assignment/data/postop_transient_coarse_poc_convergence.csv"))
    parser.add_argument("--metrics", type=Path, default=Path("assignment/data/postop_transient_coarse_poc_metrics.csv"))
    parser.add_argument("--output-directory", type=Path, default=Path("report/report/figures"))
    args = parser.parse_args()
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    convergence = args.convergence.resolve().as_posix()
    metrics = args.metrics.resolve().as_posix()

    convergence_gp = output / "assignment6_convergence.gp"
    convergence_gp.write_text(f'''set terminal cairolatex pdf color size 15cm,10cm font ",9"
set output "assignment6_convergence.tex"
set datafile separator comma
set multiplot layout 2,1 rowsfirst
set grid xtics ytics back lc rgb "#d0d0d0"
set key top right
set xrange [0:2]
set ylabel "Courant number"
set title "Adaptive timestep control"
plot "{convergence}" using 1:2 every ::1 with lines lw 1.5 lc rgb "#4d9221" title "Mean Co", \\
     "{convergence}" using 1:3 every ::1 with lines lw 1.2 lc rgb "#c51b7d" title "Maximum Co", \\
     "{convergence}" using 1:(strcol(5) eq "False" ? $3 : 1/0) every ::1 with points pt 7 ps 0.35 lc rgb "#d73027" title "Outer criterion not met"
set xlabel "Time (s)"
set ylabel "Time step (s)"
set format y "%.1t$\\times10^{{%T}}$"
set title "Physical timestep"
unset key
plot "{convergence}" using 1:4 every ::1 with lines lw 1.5 lc rgb "#2166ac"
unset multiplot
unset output
''')
    run_gnuplot(convergence_gp, output)

    response_gp = output / "assignment6_cycle_response.gp"
    response_gp.write_text(f'''set terminal cairolatex pdf color size 15cm,11cm font ",9"
set output "assignment6_cycle_response.tex"
set datafile separator comma
set datafile missing ""
set multiplot layout 2,2 rowsfirst
set grid xtics ytics back lc rgb "#d0d0d0"
set xrange [0:2]
set key top right
set ylabel "Flow rate (L/min)"
set title "Postoperative breathing-cycle response"
set xzeroaxis lw 1 lc rgb "black"
plot "{metrics}" using 1:($12*60000) every ::1 with lines lw 2 lc rgb "#2166ac" title "Section flow"
set ylabel "$\\Delta P$ (Pa)"
unset key
plot "{metrics}" using 1:11 every ::1 with lines lw 2 lc rgb "#b2182b"
set xlabel "Time (s)"
set ylabel "$R$ (Pa/(L/min))"
set yrange [0:30]
plot "{metrics}" using 1:14 every ::1 with lines lw 2 lc rgb "#4d9221" title "Transient CFD", \\
     15.153 with lines dt 2 lw 1.5 lc rgb "#444444" title "Steady coarse-mesh value"
set xlabel "Time (s)"
set ylabel "Qualitative resistance (a.u.)"
set yrange [0:3.5]
set title "Conceptual anatomical comparison (not CFD)"
plot 1.0+0.15*abs(sin(pi*x)) with lines lw 2 lc rgb "#2166ac" title "Postoperative", \\
     2.5+0.45*abs(sin(pi*x)) with lines dt 2 lw 2 lc rgb "#b2182b" title "Preoperative expectation"
unset multiplot
unset output
''')
    run_gnuplot(response_gp, output)
    print(output / "assignment6_convergence.tex")
    print(output / "assignment6_cycle_response.tex")


if __name__ == "__main__":
    main()
