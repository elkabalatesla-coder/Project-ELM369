import assert from 'node:assert/strict';
import {loadCatalog} from '../catalog.mjs';

const plugin = {manifest: {id: 'example'}};
const base = 'http://127.0.0.1:8369/index.html';
const catalog = {schemaVersion: 1, plugins: [{module: './games/example.mjs', export: 'plugins'}]};
assert.deepEqual(await loadCatalog(catalog, base, async url => {
  assert.equal(url, 'http://127.0.0.1:8369/games/example.mjs');
  return {plugins: [plugin]};
}), [plugin]);
for (const module of ['https://example.com/game.mjs', './games/../evil.mjs',
  './games/%2e%2e/evil.mjs', './games/example.mjs?x=1', '//example.com/game.mjs']) {
  await assert.rejects(loadCatalog({schemaVersion: 1, plugins: [{module, export: 'plugins'}]}, base));
}
await assert.rejects(loadCatalog({schemaVersion: 2, plugins: []}, base));
await assert.rejects(loadCatalog(catalog, base, async () => ({plugins: {}})));
console.log('Catalog tests passed');
