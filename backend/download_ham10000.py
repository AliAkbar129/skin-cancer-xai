"""Download original HAM10000 for noncommercial research; verify archives."""
import argparse,hashlib,json,zipfile
from pathlib import Path
import httpx,pandas as pd

def download(identifier,path,checksum,algorithm):
 if not path.exists():
  with httpx.stream('GET',f'https://dataverse.harvard.edu/api/access/datafile/{identifier}',follow_redirects=True,timeout=120) as r:
   r.raise_for_status()
   with path.with_suffix('.partial').open('wb') as f:
    for chunk in r.iter_bytes():f.write(chunk)
  path.with_suffix('.partial').replace(path)
 with path.open('rb') as f:digest=hashlib.file_digest(f,algorithm).hexdigest()
 if digest!=checksum:raise ValueError(f'Checksum mismatch for {path}')
 return digest
p=argparse.ArgumentParser();p.add_argument('--output',default='data/ham10000');a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
for identifier,name,md5 in [(3172585,'part1.zip','4639bfa73ab251610530a97c898e6e46'),(3172584,'part2.zip','da43d6cc50f6613013be07e8986b384b')]:
 path=out/name;download(identifier,path,md5,'md5')
 with zipfile.ZipFile(path) as archive:
  for member in archive.infolist():
   if not (out/'images'/member.filename).resolve().is_relative_to((out/'images').resolve()):raise ValueError('Unsafe archive path')
  archive.extractall(out/'images')
download(4338392,out/'metadata.tab','a430c61b1f42eb6b080ded6f7a9dbd2dd707cfe64db318e1ea62d43ab97a6505','sha256')
pd.read_csv(out/'metadata.tab',sep='\t').to_csv(out/'metadata.csv',index=False)
print('Verified original HAM10000 archives and pinned metadata response')
