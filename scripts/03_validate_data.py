import argparse, hashlib, json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--input",default="data/simulated/synthetic_sem.csv"); a=ap.parse_args()
 p=Path(a.input); p=p if p.is_absolute() else ROOT/p
 if not p.exists(): raise SystemExit(f"Missing {p}; run scripts/02_generate_synthetic.py first")
 df=pd.read_csv(p); checks=[]
 def ck(name,ok,detail): checks.append({"check":name,"passed":bool(ok),"detail":str(detail)})
 ck("N_is_1017",len(df)==1017,f"N={len(df)} (update validator if config N changes)")
 ck("unique_ID",df.respondent_id.is_unique,f"unique={df.respondent_id.nunique()}")
 ck("no_missing",df.isna().sum().sum()==0,f"missing={df.isna().sum().sum()}")
 ck("TOOL_binary",set(df.TOOL.unique()).issubset({0,1}),sorted(df.TOOL.unique().tolist()))
 likert=[c for c in df.columns if c not in ["respondent_id","TOOL"]]
 ck("Likert_1_to_5",all(df[c].between(1,5).all() for c in likert),f"columns={len(likert)}")
 required=["REPORT"]+[f"{f}{i}" for f in ["NORM","AWARE","KNOW","COMM","ATT","RESP"] for i in range(1,5)]
 ck("required_columns",set(required).issubset(df.columns),f"missing={sorted(set(required)-set(df.columns))}")
 dist=[]
 for c in likert:
  shares=df[c].value_counts(normalize=True).reindex([1,2,3,4,5],fill_value=0)
  dist.append({"variable":c,"mean":df[c].mean(),"sd":df[c].std(),"min":df[c].min(),"max":df[c].max(),"max_category_share":shares.max(),"constant":df[c].nunique()<2})
 (ROOT/"results/tables").mkdir(parents=True,exist_ok=True); (ROOT/"artifacts").mkdir(exist_ok=True)
 pd.DataFrame(dist).to_csv(ROOT/"results/tables/validation_distributions.csv",index=False)
 result=pd.DataFrame(checks); result.to_csv(ROOT/"results/tables/validation_checks.csv",index=False)
 summary={"file":str(p),"sha256":sha(p),"rows":len(df),"columns":len(df.columns),"missing_cells":int(df.isna().sum().sum()),"checks_passed":int(result.passed.sum()),"checks_total":len(result),"all_checks_passed":bool(result.passed.all()),"interpretation":"Integrity checks do not establish construct validity or SEM fit."}
 (ROOT/"artifacts/validation_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
 print(result.to_string(index=False)); print(json.dumps(summary,indent=2,ensure_ascii=False))
 if not summary["all_checks_passed"]: raise SystemExit(1)
if __name__=="__main__": main()
