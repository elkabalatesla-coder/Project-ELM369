/** Catalog entries refer only to trusted, locally installed game modules. */
export async function loadCatalog(catalog, base, importModule = url => import(url)) {
  if (catalog?.schemaVersion !== 1 || !Array.isArray(catalog.plugins)) {
    throw new Error('Unsupported game catalog');
  }
  const root = new URL('.', base);
  const plugins = [];
  for (const entry of catalog.plugins) {
    if (!entry || typeof entry.module !== 'string' ||
        !/^\.\/games\/[a-zA-Z0-9_/-]+\.mjs$/.test(entry.module) ||
        !/^[a-zA-Z][a-zA-Z0-9_]*$/.test(entry.export)) {
      throw new Error('Invalid local plugin entry');
    }
    const url = new URL(entry.module, root);
    if (url.origin !== root.origin || !url.pathname.startsWith(`${root.pathname}games/`)) {
      throw new Error('Plugin must be installed inside the local games directory');
    }
    const module = await importModule(url.href);
    const entries = module[entry.export];
    if (!Array.isArray(entries)) throw new Error('Plugin export must be an array');
    plugins.push(...entries);
  }
  return plugins;
}
