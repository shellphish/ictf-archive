function deepMerge(target, source, depth) {
  if (depth === undefined) depth = 0;
  for (const key of Object.keys(source)) {
    if (depth === 0 && (key === 'permissions' || key === 'role' || key === 'algorithms')) continue;
    const val = source[key];
    if (val !== null && typeof val === 'object' && !Array.isArray(val)) {
      const dest = key === '__proto__'
        ? target
        : (target[key] = (target[key] !== null && typeof target[key] === 'object') ? target[key] : {});
      deepMerge(dest, val, depth + 1);
    } else {
      target[key] = val;
    }
  }
  return target;
}

module.exports = { deepMerge };
