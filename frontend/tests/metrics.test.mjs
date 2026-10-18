import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { metricEntries } from '../src/utils/metrics.ts';
for (const model of ['ham10000', 'resnet18']) {
  test(`dashboard accepts actual ${model} report and excludes metadata`, () => {
    const report = JSON.parse(readFileSync(new URL(`../../evidence/${model}/evaluation.json`, import.meta.url)));
    const rows = metricEntries(report);
    assert.deepEqual(rows.map(([name]) => name), ['clean_uncalibrated', 'clean_calibrated', 'blur_radius_2', 'brightness_0.6']);
    for (const [, value] of rows) assert.equal(typeof value.macro_f1.toFixed(3), 'string');
  });
}
test('rejects malformed reports', () => {
  for (const value of [null, [], 42, { bad: { macro_f1: NaN } }]) assert.deepEqual(metricEntries(value), []);
});
