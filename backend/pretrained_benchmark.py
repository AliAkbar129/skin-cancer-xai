"""Exploratory frozen ResNet18 comparison; same lesion partitions as CPU baseline."""
import argparse,hashlib,json,time,platform
from pathlib import Path
import numpy as np,pandas as pd,torch,joblib
from PIL import Image,ImageEnhance,ImageFilter
from torchvision.models import resnet18,ResNet18_Weights
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits
from reliability import fit_temperature,calibrated_probabilities,metrics

def run(manifest,images,out):
 start=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=True);df=pd.read_csv(manifest);paths={p.stem:p for p in Path(images).rglob('*.jpg')}
 for r in df.itertuples():
  if hashlib.sha256(paths[r.image_id].read_bytes()).hexdigest()!=r.image_sha256:raise ValueError('Image changed since baseline split')
 w=ResNet18_Weights.IMAGENET1K_V1;encoder=resnet18(weights=w).eval();encoder.fc=torch.nn.Identity();transform=w.transforms()
 for p in encoder.parameters():p.requires_grad_(False)
 def extract(rows,alter=None):
  features=[]
  for first in range(0,len(rows),32):
   batch=[]
   for r in rows.iloc[first:first+32].itertuples():
    with Image.open(paths[r.image_id]) as im:
     im=im.convert('RGB');batch.append(transform(alter(im) if alter else im))
   with torch.inference_mode():features.append(encoder(torch.stack(batch)).numpy())
   if first%2048==0:print('features',first,'/',len(rows),flush=True)
  return np.concatenate(features)
 x=extract(df);y=df.dx.to_numpy();tr=df.split.eq('train').to_numpy();va=df.split.eq('validation').to_numpy();ca=df.split.eq('calibration').to_numpy();te=df.split.eq('test').to_numpy();candidates=[]
 for c in [.1,1,10]:
  m=make_pipeline(StandardScaler(),LogisticRegression(C=c,max_iter=1500,class_weight='balanced',random_state=42));m.fit(x[tr],y[tr]);f=float(f1_score(y[va],m.predict(x[va]),average='macro'));candidates.append((f,c,m));print('C',c,'validation_F1',f,flush=True)
 _,c,m=max(candidates,key=lambda a:a[0]);labels=list(m.classes_);idx=np.array([labels.index(v) for v in y]);temp=fit_temperature(m.predict_proba(x[ca]),idx[ca]);raw=m.predict_proba(x[te]);p=calibrated_probabilities(raw,temp)
 report={'clean_uncalibrated':metrics(raw,idx[te],labels),'clean_calibrated':metrics(p,idx[te],labels)}
 for name,alter in [('blur_radius_2',lambda im:im.filter(ImageFilter.GaussianBlur(2))),('brightness_0.6',lambda im:ImageEnhance.Brightness(im).enhance(.6))]:
  fx=extract(df[te],alter);report[name]=metrics(calibrated_probabilities(m.predict_proba(fx),temp),idx[te],labels)
 pred=df.loc[te,['image_id','lesion_id','dx']].copy()
 for i,label in enumerate(labels):pred['p_'+label]=p[:,i]
 pred.to_csv(out/'test_predictions.csv',index=False)
 groups=pred.lesion_id.to_numpy();unique=np.unique(groups);by={g:np.flatnonzero(groups==g) for g in unique};rng=np.random.default_rng(42);boot=[]
 for _ in range(300):
  ix=np.concatenate([by[g] for g in rng.choice(unique,len(unique),replace=True)]);boot.append(f1_score(idx[te][ix],p[ix].argmax(1),labels=list(range(len(labels))),average='macro',zero_division=0))
 report.update({'model':'Frozen ImageNet ResNet18 pooled 512D features + balanced logistic regression','pretrained_weights':'torchvision ResNet18_Weights.IMAGENET1K_V1','feature_transform':'Official weights.transforms(): resize256, center crop224, ImageNet normalization','selected_C':c,'temperature':temp,'threshold':.8,'seed':42,'split_manifest_sha256':hashlib.sha256(Path(manifest).read_bytes()).hexdigest(),'validation_macro_f1':{str(v[1]):v[0] for v in candidates},'macro_f1_lesion_bootstrap_95':list(map(float,np.quantile(boot,[.025,.975]))),'seconds':time.perf_counter()-start,'torch':torch.__version__,'platform':platform.platform(),'limitations':['Exploratory follow-up after first handcrafted baseline test results','Same held-out lesions reused; not external validation','No finetuning or CNN-ViT reproduction','No clinical or patient-disjoint guarantee','Center crop may omit lesion boundaries']})
 (out/'evaluation.json').write_text(json.dumps(report,indent=2));joblib.dump({'schema_version':1,'data_mode':'HAM10000','feature_extractor':'resnet18_global','model_type':report['model'],'pipeline':m,'temperature':temp,'threshold':.8,'metrics':report},out/'baseline.joblib');print(json.dumps(report),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--images',required=True);p.add_argument('--output',default='artifacts/resnet18');a=p.parse_args();torch.set_num_threads(2)
 with threadpool_limits(limits=2):run(a.manifest,a.images,a.output)
