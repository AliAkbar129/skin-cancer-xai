export type Metric = { n:number; macro_f1:number; balanced_accuracy:number; coverage:number; accepted_error:number|null; ece_10_equal_width_bins:number };
export function metricEntries(report: unknown): [string, Metric][] {
  if (!report || typeof report !== 'object' || Array.isArray(report)) return [];
  return Object.entries(report).filter((entry): entry is [string, Metric] => {
    const value = entry[1];
    if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
    const numeric = ['n', 'macro_f1', 'balanced_accuracy', 'coverage', 'ece_10_equal_width_bins'];
    return numeric.every(key => typeof value[key] === 'number' && Number.isFinite(value[key]))
      && (value.accepted_error === null || (typeof value.accepted_error === 'number' && Number.isFinite(value.accepted_error)));
  });
}
