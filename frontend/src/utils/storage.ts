export interface ScanRecord {
  id: string;
  date: string;
  prediction: string;
  confidence: number;
  uncertainty: number;
  imageUrl?: string;
}

export function saveScanRecord(record: Omit<ScanRecord, 'id' | 'date'>) {
  const current = getScanRecords();
  const newRecord: ScanRecord = {
    ...record,
    id: `PT-${Math.floor(1000 + Math.random() * 9000)}`,
    date: new Date().toISOString(),
  };
  
  // Keep the latest 50 scans
  const updated = [newRecord, ...current].slice(0, 50);
  localStorage.setItem('dermoxai_scans', JSON.stringify(updated));
  return newRecord;
}

export function getScanRecords(): ScanRecord[] {
  const stored = localStorage.getItem('dermoxai_scans');
  if (!stored) return [];
  try {
    return JSON.parse(stored);
  } catch (e) {
    return [];
  }
}
