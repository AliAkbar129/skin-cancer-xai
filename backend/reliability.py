"""CPU image-feature baseline and held-out reliability evaluation."""
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.metrics import balanced_accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split

LABELS = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

def grouped_split(metadata, seed=42):
    required = {'image_id', 'lesion_id', 'dx'}
    if not required <= set(metadata): raise ValueError('Missing image_id, lesion_id or dx')
    if metadata[list(required)].isna().any().any() or metadata.image_id.duplicated().any():
        raise ValueError('Null fields or duplicate image IDs')
    if not set(metadata.dx) <= set(LABELS): raise ValueError('Unexpected label')
    if metadata.groupby('lesion_id').dx.nunique().max() != 1: raise ValueError('Conflicting lesion labels')
    groups = metadata[['lesion_id', 'dx']].drop_duplicates().sort_values('lesion_id')
    train, rest = train_test_split(groups, test_size=.4, stratify=groups.dx, random_state=seed)
    val, rest = train_test_split(rest, test_size=.625, stratify=rest.dx, random_state=seed)
    cal, test = train_test_split(rest, test_size=.6, stratify=rest.dx, random_state=seed)
    assignment = {g: name for name, part in [('train',train),('validation',val),('calibration',cal),('test',test)] for g in part.lesion_id}
    result = metadata.copy(); result['split'] = result.lesion_id.map(assignment)
    return result

def image_features(image):
    a = np.asarray(image.convert('RGB').resize((128,128)), dtype=float) / 255
    hist = [np.histogram(a[:,:,i], bins=24, range=(0,1))[0] / (128*128) for i in range(3)]
    gy,gx = np.gradient(a.mean(axis=2)); mag = np.sqrt(gx*gx+gy*gy)
    hist.append(np.histogram(mag,bins=24,range=(0,1))[0] / (128*128))
    return np.concatenate(hist+[a.mean(axis=(0,1)),a.std(axis=(0,1))])

def calibrated_probabilities(probabilities, temperature=1.):
    p=np.asarray(probabilities,dtype=float)
    if p.ndim!=2 or not len(p) or not np.isfinite(p).all() or (p<0).any() or not np.allclose(p.sum(axis=1),1):
        raise ValueError('Expected finite normalized probabilities')
    if not np.isfinite(temperature) or temperature<=0: raise ValueError('Invalid temperature')
    z=np.log(np.clip(p,1e-12,1))/temperature; z-=z.max(axis=1,keepdims=True)
    p=np.exp(z); return p/p.sum(axis=1,keepdims=True)

def fit_temperature(p,y):
    y=np.asarray(y,dtype=int)
    def loss(t): return -np.log(np.clip(calibrated_probabilities(p,t)[np.arange(len(y)),y],1e-12,1)).mean()
    return float(minimize_scalar(loss,bounds=(.1,10),method='bounded').x)

def metrics(p,y,labels,threshold=.8):
    p=calibrated_probabilities(p); y=np.asarray(y,dtype=int)
    pred=p.argmax(axis=1); conf=p.max(axis=1); correct=pred==y; ece=0.
    for i in range(10):
        mask=(conf>=i/10)&(conf<(i+1)/10 if i<9 else conf<=1)
        if mask.any(): ece+=mask.mean()*abs(correct[mask].mean()-conf[mask].mean())
    accepted=conf>=threshold; curve=[]
    for t in np.linspace(0,1,21):
        m=conf>=t; curve.append({'threshold':float(t),'coverage':float(m.mean()),'error':float((~correct[m]).mean()) if m.any() else None})
    return {'n':len(y),'macro_f1':float(f1_score(y,pred,labels=list(range(len(labels))),average='macro',zero_division=0)),
            'balanced_accuracy':float(balanced_accuracy_score(y,pred)),'brier':float(((p-np.eye(len(labels))[y])**2).sum(axis=1).mean()),
            'ece_10_equal_width_bins':float(ece),'coverage':float(accepted.mean()),'accepted_error':float((~correct[accepted]).mean()) if accepted.any() else None,
            'confusion_matrix':confusion_matrix(y,pred,labels=list(range(len(labels)))).tolist(),'labels':list(labels),'risk_coverage':curve,
            'class_support':{l:int((y==i).sum()) for i,l in enumerate(labels)},
            'class_coverage':{l:float(accepted[y==i].mean()) if (y==i).any() else None for i,l in enumerate(labels)}}
