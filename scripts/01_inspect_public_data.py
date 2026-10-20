import argparse, hashlib
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--input",default="data/raw/public"); a=ap.parse_args()
 folder=Path(a.input); folder=folder if folder.is_absolute() else ROOT/folder
 if not folder.exists(): raise SystemExit(f"Folder not found: {folder}")
 rows=[]
 for p in sorted(folder.rglob("*")):
  if not p.is_file() or p.name.startswith("~$"): continue
  common={"file":str(p),"bytes":p.stat().st_size,"sha256":sha(p),"inspected_utc":datetime.now(timezone.utc).isoformat()}
  try:
   if p.suffix.lower()==".csv":
    d=pd.read_csv(p,nrows=100000,low_memory=False); rows.append({**common,"sheet":"","rows_inspected":len(d),"columns_n":len(d.columns),"columns":" | ".join(map(str,d.columns)),"dtypes":str(d.dtypes.to_dict()),"missing_rate":float(d.isna().mean().mean())})
   elif p.suffix.lower() in [".xlsx",".xlsm"]:
    for sh in pd.ExcelFile(p).sheet_names:
     d=pd.read_excel(p,sheet_name=sh,nrows=100000); rows.append({**common,"sheet":sh,"rows_inspected":len(d),"columns_n":len(d.columns),"columns":" | ".join(map(str,d.columns)),"dtypes":str(d.dtypes.to_dict()),"missing_rate":float(d.isna().mean().mean())})
  except Exception as e: rows.append({**common,"error":repr(e)})
 out=ROOT/"results/tables/public_data_inventory.csv"; out.parent.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(out,index=False,encoding="utf-8")
 print(f"Inventory saved to {out}\\nFiles/sheets inspected: {len(rows)}")
if __name__=="__main__": main()
