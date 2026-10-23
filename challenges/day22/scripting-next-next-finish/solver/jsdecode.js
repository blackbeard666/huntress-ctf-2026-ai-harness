// Sandboxed descriptor recovery for inert WSH JScript fixtures: runs the file in an empty vm context (no require,
// no WScript/ActiveXObject, no network), then calls each top-level function with eval swapped for a capture.
// Each file gets its own context. The plan is the first captured eval text (or string return value) that parses as an object with "steps".
const vm = require('vm'), fs = require('fs');
function decode(path) {
const src = fs.readFileSync(path, 'utf8');
const captured = [];
const ctx = vm.createContext({});
try { vm.runInContext(src, ctx, {timeout: 3000}); } catch (e) {}
const realEval = vm.runInContext('eval', ctx);
ctx.eval = function (s) { captured.push(String(s)); return realEval(s); };
const fns = Object.keys(ctx).filter(k => typeof ctx[k] === 'function' && k !== 'eval');
// eval users first (the inspect function), then the rest (recover functions return the JSON text directly)
fns.sort((a, b) => /\beval\s*\(/.test(String(ctx[b])) - /\beval\s*\(/.test(String(ctx[a])));
function parse(s) {
  const t = String(s).trim().replace(/^\(([\s\S]*)\)$/, '$1');
  try { return JSON.parse(t); } catch (e) {}
  try { return JSON.parse(JSON.stringify(vm.runInNewContext('(' + t + ')', {}, {timeout: 1000}))); } catch (e) {}
  return null;
}
let out = null;
for (const k of fns) {
  let r;
  try { r = vm.runInContext(k + '()', ctx, {timeout: 3000}); } catch (e) {}
  for (const s of captured.concat(typeof r === 'string' ? [r] : [])) {
    const o = parse(s);
    if (o && typeof o === 'object' && o.steps) { out = o; break; }
  }
  if (out) break;
}
return out;
}
// one path -> the plan; several paths -> {path: plan} (one node start for the whole archive)
const paths = process.argv.slice(2);
if (paths.length === 1) process.stdout.write(JSON.stringify(decode(paths[0])));
else process.stdout.write(JSON.stringify(Object.fromEntries(paths.map(p => {
  try { return [p, decode(p)]; } catch (e) { return [p, null]; }
}))));
