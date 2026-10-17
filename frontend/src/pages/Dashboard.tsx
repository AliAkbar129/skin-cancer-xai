import { useEffect, useState } from 'react';
import axios from 'axios';

type Metric = { n:number; macro_f1:number; balanced_accuracy:number; coverage:number; accepted_error:number|null; ece_10_equal_width_bins:number };
type Status = { ready:boolean; reason?:string; model_type?:string; sha256?:string; metrics:Record<string,Metric>|null };
export function Dashboard(){
 const [status,setStatus]=useState<Status|null>(null); const [error,setError]=useState('');
 const refresh=()=>{setError(''); axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/model/status`).then(r=>setStatus(r.data)).catch(()=>setError('Model service unavailable. No evaluation results can be verified.'));};
 useEffect(refresh,[]);
 return <div className="max-w-6xl mx-auto space-y-6">
  <div className="flex flex-wrap gap-4 justify-between"><div><p className="text-blue-400 text-sm">RESEARCH WORKSPACE</p><h1 className="text-3xl font-bold">DermoAI Reliability Lab</h1></div><button onClick={refresh} className="rounded-lg bg-blue-600 px-4 py-2">Refresh evidence</button></div>
  <p className="text-gray-400">Evaluate a trained baseline, calibration and selective prediction. This application does not provide clinical diagnoses.</p>
  {error&&<p role="alert" className="p-4 border border-red-400 rounded-lg">{error}</p>}
  {!status&&!error&&<p role="status">Checking installed model…</p>}
  {status&&!status.ready&&<section className="glass-panel p-6 space-y-3"><h2 className="text-xl">Training required</h2><p>{status.reason}</p><p className="text-gray-400">No accuracy, patient counts or predictions are fabricated. Follow the README to train on your licensed HAM10000 copy.</p></section>}
  {status?.ready&&<><section className="glass-panel p-6"><h2>{status.model_type}</h2><p className="break-all text-xs text-gray-400 mt-2">Artifact SHA-256: {status.sha256}</p></section>
  <div className="overflow-x-auto"><table className="w-full text-left"><caption className="text-left py-3">Measured held-out results — each corruption uses the same test images</caption><thead><tr>{['Experiment','Images','Macro F1','Coverage','Accepted error','ECE'].map(x=><th className="p-3" key={x}>{x}</th>)}</tr></thead><tbody>{Object.entries(status.metrics||{}).map(([name,m])=><tr key={name} className="border-t border-white/10"><td className="p-3">{name}</td><td>{m.n}</td><td>{m.macro_f1.toFixed(3)}</td><td>{(m.coverage*100).toFixed(1)}%</td><td>{m.accepted_error===null?'No accepted predictions':m.accepted_error.toFixed(3)}</td><td>{m.ece_10_equal_width_bins.toFixed(3)}</td></tr>)}</tbody></table></div></>}
  <section className="glass-panel p-6"><h2 className="font-semibold">Evidence boundaries</h2><p className="text-gray-400 mt-2">The first baseline uses RGB and gradient features with logistic regression. Hybrid CNN/ViT training, external validation, clinical evaluation and explanation comparisons remain separate work. Confidence is not a guarantee of correctness.</p></section>
 </div>;
}
