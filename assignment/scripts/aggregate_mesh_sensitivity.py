#!/usr/bin/env python3
"""Aggregate fixed CFD metrics and generate Assignment 5 Gnuplot figures."""
import argparse,csv,json,re,subprocess
from pathlib import Path

DEFAULT=[("postop_hxt_025",0.25),("postop_hxt_020",0.20),("postop_hxt_015",0.15),("postop_hxt_012",0.12)]
METRICS=[("resistance_pa_per_l_min","Resistance (Pa/(L/min))"),("right_lung_fraction_percent","Right-lung flow fraction (\\%)"),("right_superior_share_percent","Right-superior share of right flow (\\%)"),("matched_peak_velocity_m_s","Matched-section peak velocity (m/s)")]

def parse_case(case,size,data_dir,results):
    m=json.loads((data_dir/f"{case}_cfd_metrics.json").read_text()); f=json.loads((data_dir/f"{case}_flow_distribution.json").read_text()); log=(results/case/"log.checkMesh.final").read_text(errors="replace"); solver=(results/case/"log.simpleFoam.parallel").read_text(errors="replace")
    def number(pattern,cast=float):
        x=re.search(pattern,log); return cast(x.group(1)) if x else None
    iterations=[int(x) for x in re.findall(r"^Time = (\d+)$",solver,re.M)]
    execution=[float(x) for x in re.findall(r"ExecutionTime = ([0-9.eE+-]+)",solver)]
    region=m["region_metrics"]; matched=m["planes"]["matched"]
    return {"case":case,"mesh_size_mm":size,"cells":number(r"cells:\s+(\d+)",int),"points":number(r"points:\s+(\d+)",int),"max_aspect_ratio":number(r"Max aspect ratio =\s*([^ ]+)"),"max_non_orthogonality_deg":number(r"Mesh non-orthogonality Max:\s*([^ ]+)"),"severe_non_orthogonal_faces":number(r"Number of severely non-orthogonal \(> 70 degrees\) faces:\s*(\d+)",int),"max_skewness":number(r"Max skewness =\s*([^ ]+)"),"minimum_cell_volume_m3":number(r"Min volume =\s*([^ ]+)"),"final_iteration":max(iterations) if iterations else None,"execution_time_s":execution[-1] if execution else None,"pressure_drop_pa":region["pressure_drop_pa"],"resistance_pa_per_l_min":region["local_resistance_pa_per_l_min"],"matched_mean_axial_velocity_m_s":matched["area_average_axial_velocity_m_s"],"matched_peak_velocity_m_s":matched["peak_velocity_magnitude_m_s"],"right_lung_fraction_percent":f["lungs"]["right"]["fraction_percent"],"left_lung_fraction_percent":f["lungs"]["left"]["fraction_percent"],"right_superior_share_percent":f["right_superior_share_percent"],"mass_imbalance_percent":f["relative_mass_imbalance_percent"]}

def plot(csv_path,tex_path,difference=False):
    report=tex_path.resolve().parents[1]; out=tex_path.resolve().relative_to(report).as_posix(); gp=tex_path.resolve().with_suffix('.gp'); cols={"resistance_pa_per_l_min":13,"right_lung_fraction_percent":16,"right_superior_share_percent":18,"matched_peak_velocity_m_s":15}; suffix="_difference_percent"; diffcols={k:20+i for i,(k,_) in enumerate(METRICS)}
    commands=[]
    for key,label in METRICS:
        col=diffcols[key] if difference else cols[key]; ylabel="Difference from finest mesh (\\%)" if difference else label
        commands.append(f'''set ylabel "{ylabel}"\nset title "{label}"\nplot "{csv_path.resolve().as_posix()}" using 3:{col} every ::1 with linespoints lw 2 pt 7 notitle''')
    script=f'''set terminal cairolatex pdf color size 16cm,13cm font ",9"\nset output "{out}"\nset datafile separator comma\nset multiplot layout 2,2 rowsfirst\nset grid xtics ytics back lc rgb "#d0d0d0"\nset xlabel "Number of volume cells"\nset format x "%.1t$\\times10^{{%T}}$"\n'''+'\n'.join(commands)+'''\nunset multiplot\nunset output\n'''; gp.write_text(script); subprocess.run(["gnuplot",str(gp)],cwd=report,check=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--case",action="append",help="CASE:SIZE_MM"); ap.add_argument("--data-dir",type=Path,default=Path("assignment/data")); ap.add_argument("--results-root",type=Path,default=Path("results")); a=ap.parse_args(); cases=DEFAULT if not a.case else [(x.rsplit(':',1)[0],float(x.rsplit(':',1)[1])) for x in a.case]
    rows=[parse_case(c,s,a.data_dir,a.results_root) for c,s in cases]; rows.sort(key=lambda r:r["cells"]); reference=max(rows,key=lambda r:r["cells"])
    for row in rows:
        for key,_ in METRICS:
            row[f"{key}_difference_percent"]=100*abs(row[key]-reference[key])/abs(reference[key]) if reference[key] else 0.0
        row["right_lung_fraction_percentage_point_difference"]=abs(row["right_lung_fraction_percent"]-reference["right_lung_fraction_percent"])
    fields=list(rows[0]); csv_path=a.data_dir/"mesh_sensitivity.csv"; a.data_dir.mkdir(parents=True,exist_ok=True)
    with csv_path.open('w',newline='') as out: w=csv.DictWriter(out,fieldnames=fields); w.writeheader(); w.writerows(rows)
    (a.data_dir/"mesh_sensitivity.json").write_text(json.dumps({"schema_version":1,"reference_case":reference["case"],"difference_formula":"abs(value-reference)/abs(reference)*100","rows":rows},indent=2)+"\n")
    plot(csv_path,Path("report/figures/assignment5_mesh_metrics.tex")); plot(csv_path,Path("report/figures/assignment5_mesh_differences.tex"),True); print(csv_path); print("Reference:",reference["case"])
if __name__=="__main__": main()
