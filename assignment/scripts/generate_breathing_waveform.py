#!/usr/bin/env python3
"""Generate the sinusoidal infant breathing waveform and report figure."""
import argparse, csv, math, subprocess
from pathlib import Path


def main():
    p=argparse.ArgumentParser(); p.add_argument("--csv",type=Path,default=Path("assignment/data/breathing_waveform.csv")); p.add_argument("--table",type=Path,default=Path("openFOAM/postop_transient/constant/breathingFlowRate.table")); p.add_argument("--plot",type=Path,default=Path("report/figures/assignment6_breathing_waveform.tex")); p.add_argument("--period",type=float,default=2.0); p.add_argument("--minute-volume",type=float,default=2.0,help="L/min"); p.add_argument("--samples",type=int,default=401); a=p.parse_args()
    peak=a.minute_volume*math.pi/60000.0
    rows=[]
    for i in range(a.samples):
        t=a.period*i/(a.samples-1); q=peak*math.sin(2*math.pi*t/a.period)
        if i in (0,a.samples-1): q=0.0
        rows.append((t,q,q*60000.0))
    a.csv.parent.mkdir(parents=True,exist_ok=True)
    with a.csv.open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["time_s","flow_rate_m3_s","flow_rate_L_min"]); w.writerows(rows)
    a.table.parent.mkdir(parents=True,exist_ok=True)
    # Supply the complete Function1 entry through the include so OpenFOAM
    # parses it at dictionary-entry level rather than inside a primitive value.
    a.table.write_text(
        "volumetricFlowRate table\n(\n"
        + "".join(f"    ({t:.8f} {q:.12g})\n" for t, q, _ in rows)
        + ");\n"
    )
    a.plot.parent.mkdir(parents=True,exist_ok=True); report=a.plot.resolve().parents[1]; out=a.plot.resolve().relative_to(report).as_posix(); gp=a.plot.resolve().with_suffix('.gp')
    gp.write_text(f'''set terminal cairolatex pdf color size 15cm,8cm font ",10"\nset output "{out}"\nset datafile separator comma\nset grid xtics ytics back lc rgb "#d0d0d0"\nset key off\nset xlabel "Time (s)"\nset ylabel "Inlet flow rate (L/min)"\nset title "Sinusoidal breathing waveform"\nset xzeroaxis lw 1 lc rgb "black"\nplot "{a.csv.resolve().as_posix()}" using 1:3 every ::1 with lines lw 2.2 lc rgb "#2166ac"\nunset output\n''')
    subprocess.run(["gnuplot",str(gp)],cwd=report,check=True)
    tidal=peak*a.period/math.pi
    print(f"Peak: {peak:.8g} m3/s ({peak*60000:.4f} L/min)"); print(f"Tidal volume: {tidal*1e6:.3f} mL"); print(a.csv); print(a.table); print(a.plot)
if __name__=="__main__": main()
