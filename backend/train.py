"""Train/evaluate a real CPU baseline on user-provided HAM10000 images."""
import argparse,hashlib,json,platform,time
from pathlib import Path
import joblib,numpy as np,pandas as pd
from PIL import Image,ImageFilter,ImageEnhance
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from reliability import grouped_split,image_features,fit_temperature,calibrated_probabilities,metrics

def run(metadata_path,image_dir,output,seed=42,data_mode="HAM10000"):
    start=time.perf_counter(); output=Path(output); output.mkdir(parents=True,exist_ok=True)
    meta=grouped_split(pd.read_csv(metadata_path),seed)
    paths={p.stem:p for p in Path(image_dir).rglob('*.jpg')}
    if set(meta.image_id)-set(paths): raise ValueError('Images missing for metadata records')
    hashes={}; features=[]
    for row in meta.itertuples():
        path=paths[row.image_id]; h=hashlib.sha256(path.read_bytes()).hexdigest()
        if h in hashes and hashes[h]!=row.split: raise ValueError('Duplicate image across partitions')
        hashes[h]=row.split
        with Image.open(path) as im: features.append(image_features(im))
    x=np.array(features); y=meta.dx.to_numpy()
    train=meta.split.eq('train').to_numpy(); val=meta.split.eq('validation').to_numpy(); candidates=[]
    for c in [.1,1,10]:
        model=make_pipeline(StandardScaler(),LogisticRegression(C=c,class_weight='balanced',max_iter=1500,random_state=seed))
        model.fit(x[train],y[train]); score=f1_score(y[val],model.predict(x[val]),average='macro',zero_division=0)
        candidates.append((score,c,model))
    _,c,model=max(candidates,key=lambda item:item[0]); labels=list(model.classes_); indices=np.array([labels.index(v) for v in y])
    cal=meta.split.eq('calibration').to_numpy(); test=meta.split.eq('test').to_numpy()
    temp=fit_temperature(model.predict_proba(x[cal]),indices[cal]); threshold=.8
    raw=model.predict_proba(x[test]); p=calibrated_probabilities(raw,temp)
    report={'clean_uncalibrated':metrics(raw,indices[test],labels,threshold),'clean_calibrated':metrics(p,indices[test],labels,threshold)}
    for name,transform in [('blur_radius_2',lambda im:im.filter(ImageFilter.GaussianBlur(2))),('brightness_0.6',lambda im:ImageEnhance.Brightness(im).enhance(.6))]:
        fx=[]
        for row in meta[test].itertuples():
            with Image.open(paths[row.image_id]) as im: fx.append(image_features(transform(im.convert('RGB'))))
        report[name]=metrics(calibrated_probabilities(model.predict_proba(fx),temp),indices[test],labels,threshold)
    meta.to_csv(output/'split_manifest.csv',index=False)
    artifact={'schema_version':1,'data_mode':data_mode,'model_type':'RGB-gradient logistic regression baseline','pipeline':model,
              'temperature':temp,'threshold':threshold,'metrics':report,'seed':seed,'selected_C':c,
              'metadata_sha256':hashlib.sha256(Path(metadata_path).read_bytes()).hexdigest()}
    joblib.dump(artifact,output/'baseline.joblib')
    report.update({'seed':seed,'selected_C':c,'temperature':temp,'threshold':threshold,'seconds':time.perf_counter()-start,
                   'platform':platform.platform(),'data_mode':data_mode,'limitations':['No clinical validation','No patient-disjoint claim','No external validation','No CNN trained in this run']})
    (output/'evaluation.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({'output':str(output),'clean_macro_f1':report['clean_calibrated']['macro_f1']}))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--metadata',required=True); ap.add_argument('--images',required=True); ap.add_argument('--output',default='artifacts'); ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--data-mode',choices=['HAM10000','synthetic_fixture'],required=True)
    a=ap.parse_args(); run(a.metadata,a.images,a.output,a.seed,a.data_mode)
