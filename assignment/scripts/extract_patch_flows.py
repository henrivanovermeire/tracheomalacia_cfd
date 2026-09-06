#!/usr/bin/env python3
"""Integrate OpenFOAM inlet/outlet fluxes and save anatomical flow fractions."""
import argparse, json, re, subprocess
from pathlib import Path

PATCHES = {
    "inlet": ("tracheal inlet", 25),
    "outlet_1": ("right superior lobar bronchus", 23),
    "outlet_2": ("right inferior lobar bronchus", 24),
    "outlet_3": ("left main bronchus", 22),
}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("case"); ap.add_argument("--results-root",type=Path,default=Path("results")); ap.add_argument("--output-dir",type=Path,default=Path("assignment/data")); ap.add_argument("--image",default="opencfd/openfoam-default:latest"); a=ap.parse_args()
    case_dir=(a.results_root/a.case).resolve()
    if not (case_dir/f"{a.case}.foam").exists(): raise SystemExit(f"Missing reconstructed case: {case_dir}")
    flows={}; final_time=None
    for patch in PATCHES:
        command=["docker","run","--rm","--user","0:0","--env","HOME=/tmp","--volume",f"{a.results_root.resolve()}:/cases","--workdir",f"/cases/{a.case}",a.image,"bash","-c",f"if ! command -v postProcess >/dev/null 2>&1; then source /usr/lib/openfoam/openfoam2512/etc/bashrc; fi; cd /cases/{a.case}; postProcess -func 'flowRatePatch(name={patch})' -latestTime"]
        run=subprocess.run(command,text=True,capture_output=True)
        if run.returncode: raise SystemExit(run.stdout+run.stderr)
        match=re.search(rf"sum\({re.escape(patch)}\) of phi = ([0-9.eE+-]+)",run.stdout+run.stderr)
        time_match=re.search(r"Time = ([0-9.eE+-]+)",run.stdout+run.stderr)
        if not match: raise SystemExit(f"Could not parse flow for {patch}")
        flows[patch]=float(match.group(1)); final_time=float(time_match.group(1)) if time_match else final_time
    inlet_magnitude=abs(flows["inlet"]); outlets={}
    for patch in ("outlet_1","outlet_2","outlet_3"):
        anatomy,surface=PATCHES[patch]; outlets[patch]={"anatomy":anatomy,"surface_id":surface,"flow_rate_m3_s":flows[patch],"fraction_percent":100*flows[patch]/inlet_magnitude}
    right=flows["outlet_1"]+flows["outlet_2"]; left=flows["outlet_3"]; total=right+left
    result={"schema_version":1,"case":a.case,"time":final_time,"sign_convention":"outward patch-normal flux","inlet":{"flow_rate_m3_s":flows["inlet"]},"outlets":outlets,"lungs":{"right":{"patches":["outlet_1","outlet_2"],"flow_rate_m3_s":right,"fraction_percent":100*right/inlet_magnitude},"left":{"patches":["outlet_3"],"flow_rate_m3_s":left,"fraction_percent":100*left/inlet_magnitude}},"right_superior_share_percent":100*flows["outlet_1"]/right,"total_outlet_flow_rate_m3_s":total,"absolute_mass_imbalance_m3_s":abs(total-inlet_magnitude),"relative_mass_imbalance_percent":100*abs(total-inlet_magnitude)/inlet_magnitude}
    a.output_dir.mkdir(parents=True,exist_ok=True); out=a.output_dir/f"{a.case}_flow_distribution.json"; out.write_text(json.dumps(result,indent=2)+"\n"); print(out); print(f"Right={result['lungs']['right']['fraction_percent']:.6f}% Left={result['lungs']['left']['fraction_percent']:.6f}%")
if __name__=="__main__": main()
