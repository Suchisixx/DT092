import argparse, hashlib, json, platform, sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np, pandas as pd, yaml
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--config",default="config/model_config.yml"); a=ap.parse_args()
 cp=Path(a.config); cp=cp if cp.is_absolute() else ROOT/cp
 cfg=yaml.safe_load(cp.read_text(encoding="utf-8")); p=cfg["project"]; n=int(p["n"]); rng=np.random.default_rng(int(p["seed"]))
 out=Path(p["output_csv"]); out=out if out.is_absolute() else ROOT/out; out.parent.mkdir(parents=True,exist_ok=True)
 (ROOT/"results/logs").mkdir(parents=True,exist_ok=True); (ROOT/"results/tables").mkdir(parents=True,exist_ok=True); (ROOT/"artifacts").mkdir(exist_ok=True)
 exo_names=["NORM","AWARE","KNOW","COMM"]
 corr=np.array([[1,.30,.25,.20],[.30,1,.35,.25],[.25,.35,1,.30],[.20,.25,.30,1.]])
 if np.linalg.eigvalsh(corr).min()<=0: raise ValueError("Exogenous correlation matrix is not positive definite")
 exo=rng.multivariate_normal(np.zeros(4),corr,size=n); lat={k:exo[:,i] for i,k in enumerate(exo_names)}
 def make_latent(betas):
  signal=sum(float(b)*lat[k] for k,b in betas.items())
  y=signal+rng.normal(0,np.sqrt(max(.15,1-min(float(np.var(signal)),.85))),n)
  return (y-y.mean())/(y.std() or 1)
 st=cfg["structural"]
 lat["ATT"]=make_latent(st["ATT"]["predictors"]); lat["RESP"]=make_latent(st["RESP"]["predictors"])
 tool=rng.binomial(1,float(st.get("tool_probability",.65)),n); lat["TOOL"]=tool.astype(float)
 lat["COMMxTOOL"]=(lat["COMM"]-lat["COMM"].mean())*(tool-tool.mean())
 lat["REPORT"]=make_latent(st["REPORT"]["predictors"])
 df=pd.DataFrame({"respondent_id":[f"SYN{i:04d}" for i in range(1,n+1)]})
 th=np.array(cfg["ordinal"]["thresholds"],float); lo=int(cfg["ordinal"]["likert_min"]); hi=int(cfg["ordinal"]["likert_max"])
 for factor,spec in cfg["measurement"].items():
  loading=float(spec["loading"])
  for j in range(1,int(spec["items"])+1):
   x=loading*lat[factor]+rng.normal(0,np.sqrt(max(.01,1-loading**2)),n)
   df[f"{factor}{j}"]=np.clip(np.digitize(x,th)+lo,lo,hi).astype(int)
 df["TOOL"]=tool.astype(int)
 df["REPORT"]=np.clip(np.digitize(lat["REPORT"]+rng.normal(0,.45,n),th)+lo,lo,hi).astype(int)
 df.to_csv(out,index=False,encoding="utf-8")
 desc=df.drop(columns=["respondent_id"]).describe().T; desc["missing_n"]=df.isna().sum(); desc.to_csv(ROOT/"results/tables/synthetic_item_descriptives.csv",encoding="utf-8")
 freq=[]
 for c in df.columns[1:]:
  for val,count in df[c].value_counts().sort_index().items(): freq.append({"variable":c,"value":val,"count":int(count),"proportion":count/n})
 pd.DataFrame(freq).to_csv(ROOT/"results/tables/synthetic_value_frequencies.csv",index=False)
 manifest={"dataset_name":out.name,"dataset_type":"SYNTHETIC_SIMULATED_NOT_REAL_RESPONDENTS","n_rows":len(df),"n_columns":len(df.columns),"source":"scripts/02_generate_synthetic.py","source_url":None,"license":"Project-generated synthetic data","generated_utc":datetime.now(timezone.utc).isoformat(),"seed":int(p["seed"]),"simulation_version":p["simulation_version"],"config_sha256":sha(cp),"output_sha256":sha(out),"python_version":sys.version,"platform":platform.platform(),"missing_cells":int(df.isna().sum().sum()),"notes":"Simulation assumptions only; not real respondents or empirical estimates"}
 (ROOT/"artifacts/synthetic_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
 log=f"Generated {out}\\nN={len(df)}, columns={len(df.columns)}\\nseed={p['seed']}\\nSHA256={manifest['output_sha256']}\\nSynthetic only; not real respondents.\\n"
 (ROOT/"results/logs/generate_synthetic.log").write_text(log,encoding="utf-8"); print(log)
if __name__=="__main__": main()
